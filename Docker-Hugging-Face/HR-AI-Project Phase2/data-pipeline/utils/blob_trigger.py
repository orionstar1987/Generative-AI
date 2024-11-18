import logging
import os
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from azure.data.tables import TableClient
from .table import get_records, update_last_processing
from .converter import convert_to_serializable
TableClient

async def process_blob(blob, process_activity):
    conn_string = os.getenv("AzureTriggerStorageConnection")
    table_service_client = TableServiceClient.from_connection_string(conn_str=conn_string)
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_string)
    table_client = table_service_client.get_table_client(table_name="filesregister")

    blob_client = blob_service_client.get_blob_client(container=blob.name.split('/')[0],
                                                      blob='/'.join(blob.name.split('/')[1:]))
    blob_properties = blob_client.get_blob_properties()

    records = get_records(table_client)
    record = [item for item in records if item['FileUrl'].replace(' ', '%20') == blob_client.url]

    logging.info(f"BLOB URL:{blob_client.url}, Item metadata: {record}")

    if record and (
            "LastProcessing" not in record[0] or record[0]["LastProcessing"] != blob_properties["last_modified"]):
        result = await process_activity(record[0])
        update_last_processing(table_client, record[0], blob_properties['last_modified'])
        logging.info(f"Direct activity processing result: {result}")


def fetch_blob_metadata(containers, all_records=False):
    conn_string = os.getenv("AzureTriggerStorageConnection")
    table_service_client = TableServiceClient.from_connection_string(conn_str=conn_string)
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_string)
    table_client = table_service_client.get_table_client(table_name="filesregister")
    results = []

    for container_name in containers:
        container_client = blob_service_client.get_container_client(container_name.split('/')[0])
        blobs = container_client.list_blobs()
        records = get_records(table_client)

        for blob in blobs:
            blob_client = container_client.get_blob_client(blob)
            blob_properties = blob_client.get_blob_properties()

            record = [
                item for item in records
                if item['FileUrl'].replace(' ', '%20') == blob_client.url
            ]

            if all_records and record:
                results.append(record[0])
            else:
                if record:
                    last_processing = record[0].get("LastProcessing")
                    last_modified = blob_properties["last_modified"]

                    if not last_processing or last_processing != last_modified:
                        results.append(record[0])
    results = [
        {**record, "LastProcessing": record["LastProcessing"].isoformat()}
        if record.get("LastProcessing") is not None
        else record
        for record in results
    ]

    return results
