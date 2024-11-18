import os
from typing import Optional

from openai import AzureOpenAI

from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery
from typing import Any

from core.loaders.config import IndexConfig, local_index_config, property_to_idx
from core.modules.utils import Translator
import logging

def nonewlines(s: str) -> str:
    return s.replace('\n', ' ').replace('\r', ' ')


def create_embedding(text) -> list[float]:
    client = AzureOpenAI(api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                         api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
                         azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
                         )

    deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', "emb-deployment")

    print(f"Embedding configuration: E:{os.getenv('AZURE_OPENAI_ENDPOINT')} |  D:{deployment}")
    response = client.embeddings.create(
        input=text,
        model=deployment
    )
    return response.data[0].embedding


class IndexManager:

    def __init__(self,
                 search_endpoint: str,
                 search_credential: Any,
                 translator: Translator,
                 property_to_index_mapping: dict = property_to_idx):
        """

        :param embedding_model: langchain interface for embedding model
        :type embedding_model: langchain_openai.embeddings.AzureOpenAIEmbeddings
        :param index_config: configuration of SQL query templates for each category
        :type index_config: core.loaders.config.IndexConfig
        """
        super().__init__()

        self.property_to_index_mapping = property_to_index_mapping
        self.search_endpoint = search_endpoint
        self.search_credential = search_credential
        self.translator = translator

    def get_retriever(self, categories: list[str],
                      property_idx: str,
                      category_mapping: dict = None) -> list[SearchClient] | None:
        """
        Get retrievers for selected categories
        :param categories: list of categories relevant for the user message
        :type categories: list[str]
        :param category_mapping: mapping between input categories (e.g. LLM classifier output)
        and categories defined in self.context
        :type category_mapping: dict[str, str]
        :return: retriever on None
        :rtype: langchain.retrievers.EnsembleRetriever | None
        """

        print("Categories before mapping:", categories)
        if category_mapping:
            categories = [category_mapping.get(x) for x in categories]
            categories = [x for x in categories if x]
            print("Categories after mapping:", categories)

        if not categories:
            return None
        if categories == 'nothing' or categories == ["nothing"]:
            return None

        index_names = []
        for idx in self.property_to_index_mapping.get(property_idx, ['all']):
            index_names.extend([f"{cat}-{idx}" for cat in categories])

        print(f"Index names to be searched: {index_names}")

        retrievers = []
        for index in index_names:
            search_client = SearchClient(endpoint=self.search_endpoint,
                                         index_name=index,
                                         credential=self.search_credential
                                         )
            retrievers.append(search_client)

        return retrievers

    async def retrieve(self, text: str,
                 categories: list[str],
                 property_idx: str,
                 k: int = 10,
                 single_k: int = 15,
                 category_mapping: dict = None,
                 conversation_language: str = 'EN',
                 property_language: str = 'EN'
                ) -> str:
        """

        :param text: text that is used to build a search vector
        :type text: str
        :param categories: list of categories relevant for the user message
        :type categories: list[str]
        :param k: number of retrieved chunks of data (final)
        :type k: int
        :param single_k: number of nearest neighbours for retrieval (per category)
        :type single_k: int
        :param category_mapping: mapping between input categories (e.g. LLM classifier output)
        and categories defined in self.indexes
        :type category_mapping: dict[str, str]
        :return: formatted context string
        :rtype: str
        """
        categories = [x for x in categories if x]
        if not categories:
            return ""
        retrievers = self.get_retriever(categories, property_idx, category_mapping=category_mapping)
        if not retrievers:
            return ""

        try:
            search_embedding = create_embedding(text)
            vector = VectorizedQuery(vector=search_embedding, k_nearest_neighbors=single_k, fields='text_vector')
            vector_queries = [vector]
        except Exception as e:
            print(f'Exception occured when getting embeddings: {e}')
            print('Falling back to text-only search')
            vector_queries = None

        chunks = []

        for search_client in retrievers:
            search_client: SearchClient
            search_text = text
            idx_name = search_client._index_name
            # check for translation to property language
            if (conversation_language != property_language) and '_en' not in idx_name:
                search_text = self.translator(text, self.translator.lang_code_to_name.get(property_language))

            # check for translation to english
            elif '_en' not in idx_name and conversation_language != 'EN':
                search_text = self.translator(text, self.translator.lang_code_to_name.get('EN'))

            # disable hybrid search for papiamento
            if '_en' not in idx_name and conversation_language == 'CAR':
                search_text = None

            results = await search_client.search(
                search_text=search_text,
                search_fields=['content'],
                top=single_k,
                vector_queries=vector_queries,
                select=['content', 'title', 'page_number', 'property', 'url'])

            if not results:
                continue

            async for res in results:
                if (property_idx.lower() not in res['property'].lower()) and ('all' not in res['property'].lower()):
                    continue

                doc = {'content': res['content'],
                       'title': res['title'],
                       'score': res['@search.score'],
                       'page_number': res['page_number'],
                       'url': res['url']}
                chunks.append(doc)

        top_chunks = sorted(chunks, key=lambda x: x.get('score'), reverse=True)[:k]

        print([f"{chunk['title']}: {chunk['score']}" for chunk in top_chunks])
        return self._format_docs(top_chunks)

    @staticmethod
    def _format_docs(docs):
        docs_formatted = []
        for doc in docs:
            doc_formatted = f"""<<<HEADER: {doc['title']}, URL: {doc['url']}>>>
{nonewlines(doc['content'])}
"""
            docs_formatted.append(doc_formatted)

        return "\n".join([d for d in docs_formatted])


