import os
import json
from io import BytesIO
import re
from time import sleep

from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    HnswParameters
)
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import AzureOpenAI, RateLimitError
from typing import Any
from .config import property_to_idx_mapping
import base64
import hashlib
import logging


def create_search_index_if_not_exists(index_client: SearchIndexClient, index_name: str):
    if index_name not in [index.name for index in index_client.list_indexes()]:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),  #
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="text_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                            vector_search_dimensions=1536, vector_search_configuration="my-vector-config"),
            SimpleField(name="metadata", type=SearchFieldDataType.String),
            SimpleField(name="parent_id", type=SearchFieldDataType.String),
            SimpleField(name="page_number", type=SearchFieldDataType.Int32),
        ]
        vector_search = VectorSearch(
            algorithms=[
                VectorSearchAlgorithmConfiguration(
                    name="my-vector-config",
                    kind="hnsw",
                    hnsw_parameters=HnswParameters(metric="cosine")
                )
            ]
        )
        index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
        index_client.create_index(index)
        print(f"Created index: {index_name}")
    else:
        print(f"Index {index_name} already exists")


def download_blob(blob_service_client: BlobServiceClient,
                  container_name: str,
                  blob_name: str) -> BytesIO:
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob().readall()
    return BytesIO(blob_data)


def extract_text_from_pdf(pdf_buffer: BytesIO):
    with pdf_buffer as file:
        pdf_reader = PdfReader(file)
        pages = [page.extract_text() for page in pdf_reader.pages]
    return pages


def create_embedding(text):
    try:
        client = AzureOpenAI(api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                             api_version="2024-02-01",
                             azure_endpoint=os.getenv('AZURE_OPENAI_SERVICE')
                             )
        response = client.embeddings.create(
            input=text,
            model=os.getenv('EMBEDDING_MODEL', "text-embedding-ada-002"),
        )
        return response.data[0].embedding, 0, None
    except RateLimitError as e:
        return None, 1, e


def delete_parent_w_children(search_client: SearchClient,
                             parent_id: str) -> int:
    filter_expr = f"parent_id eq '{parent_id}'"
    results = search_client.search(
        search_text="*",
        filter=filter_expr,
        select=["id"],  # Only retrieve document IDs
        include_total_count=True
    )

    # Collect all document IDs
    doc_ids = [doc['id'] for doc in results]
    total_docs = len(doc_ids)
    if total_docs == 0:
        logging.info(f"No documents found with parent_id={parent_id}")
        return 0

    logging.info(f"Found {total_docs} documents to delete")
    deleted_count = 0
    try:
        results = search_client.delete_documents(documents=[{"id": doc_id} for doc_id in doc_ids])
        # Check results for any failures
        for doc_id, result in zip(doc_ids, results):
            if result.succeeded:
                deleted_count += 1
            else:
                logging.info(f"Failed to delete document {doc_id}: {result.error_message}")

    except Exception as e:
        logging.info(f"Error during deletion: {str(e)}")

    return deleted_count


def index_or_update_document(search_client: SearchClient,
                             parent_id,
                             url,
                             content,
                             embedding,
                             language,
                             topic,
                             property,
                             chunk_id,
                             page_number):

    parent_id = re.sub(r'[^a-zA-Z0-9 -]', '-', parent_id)

    document = {
        'id': f"{parent_id.replace(' ', '-')}_page_{page_number}_chunk_{chunk_id}",
        'parent_id': parent_id.replace(' ', '-'),
        'url': url,
        'content': content,
        'title': parent_id,
        'text_vector': embedding,
        'language': language,
        'topic': topic,
        'property': property,
        'page_number': page_number,
    }

    try:
        search_client.upload_documents([document])
        logging.info(f"Indexed/Updated document: {parent_id.replace(' ', '-')}_page_{page_number}_chunk_{chunk_id}")
    except Exception as e:
        logging.error(
            f"Error indexing/updating document {parent_id.replace(' ', '-')}_page_{page_number}_chunk_{chunk_id}: {str(e)}")


def process_pdf(blob_service_client: BlobServiceClient,
                search_credential: Any,
                search_endpoint: Any,
                container_name: str,
                blob_name: str,
                text_splitter: RecursiveCharacterTextSplitter,
                metadata: dict):

    # Download PDF from Blob Storage
    buffer = download_blob(blob_service_client, container_name, blob_name)

    # Extract text from PDF, page by page
    try:
        pages = extract_text_from_pdf(buffer)
    except Exception as e:
        # generic as pypdf uses version-specific errors
        logging.warning(f'Error parsing {blob_name}: {e}')
        return

    parent_id = metadata.get('FileName')
    language = metadata.get('Language')
    property = metadata.get('Property')
    topic = metadata.get('Topic')
    url = metadata.get('FileUrl').replace(' ', '%20')
    idx = property_to_idx_mapping.get(property)

    if not idx:
        if language == 'English':
            idx = 'all'
        else:
            logging.info('Unsupported language*property combination')
            return
    if idx not in ['us', 'all'] and language == 'English':
        idx += '-en'

    index_client = SearchIndexClient(endpoint=search_endpoint,
                                     credential=search_credential)

    search_client = index_client.get_search_client(f'common-files-{idx}')

    logging.info(f"Target index: common-files-{idx}")
    logging.info(f'Chunks in index before upsert: {search_client.get_document_count()}')

    # delete old entry
    try:
        cnt = delete_parent_w_children(search_client, parent_id.replace(' ', '-'))
        logging.info(f'Deleted {cnt} chunks')
    except Exception:
        logging.info("Nothing to delete")

    if os.getenv("SplitByPage") != "False":
        # Process each page
        for page_number, page_text in enumerate(pages, start=1):
            # Chunk the page text using LangChain's RecursiveCharacterTextSplitter
            chunks = text_splitter.split_text(page_text)

            # Process each chunk
            for chunk_id, chunk in enumerate(chunks):
                logging.info(f'Processing chunk {chunk_id} of page {page_number}')
                # Create embedding for the chunk
                for i in range(0, int(os.getenv("MAX_RETRIES"), 10)):
                    embedding, status, e = create_embedding(chunk)
                    if status == 0:
                        break
                    sleep(10)

                if embedding is None:
                    raise e

                # Index or update document
                index_or_update_document(search_client,
                                         parent_id,
                                         url,
                                         chunk,
                                         embedding,
                                         language,
                                         topic,
                                         property,
                                         chunk_id,
                                         page_number)

    else:
        full_text = ' '.join(pages)
        chunks = text_splitter.split_text(full_text)
        # Process each chunk
        for chunk_id, chunk in enumerate(chunks):
            logging.debug(f'Processing chunk {chunk_id} of page {0}')
            # Create embedding for the chunk
            embedding = create_embedding(chunk)
            # Index or update document
            index_or_update_document(search_client,
                                     parent_id,
                                     url,
                                     chunk,
                                     embedding,
                                     language,
                                     topic,
                                     property,
                                     chunk_id,
                                     0)


def parse_record(record: dict[str, Any],
                 search_service_name: str,
                 search_api_key: str,
                 blob_service_client: BlobServiceClient):
    blob_url = record["FileUrl"]
    container_name = blob_url.replace('https://', '').split('/')[1]
    blob_name = '/'.join(blob_url.replace('https://', '').split('/')[2:])
    endpoint = f"https://{search_service_name}.search.windows.net/"
    credential = AzureKeyCredential(search_api_key)

    # Additional split chars required for mandarin
    text_splitter = RecursiveCharacterTextSplitter(separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",
    ],
        chunk_size=int(os.getenv('ChunkSize', 1000)),
        chunk_overlap=int(os.getenv('ChunkOverlap', 100)))

    logging.info(f'Starting parsing process for {blob_name}')
    process_pdf(blob_service_client, credential, endpoint, container_name, blob_name, text_splitter, record)
