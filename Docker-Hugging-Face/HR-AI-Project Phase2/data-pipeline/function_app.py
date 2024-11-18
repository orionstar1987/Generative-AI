import azure.functions as func
import azure.durable_functions as df
import openai
import os
import logging

from azure.storage.blob import BlobServiceClient

from core.utils import parse_record
from utils.blob_trigger import process_blob, fetch_blob_metadata

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="health")
def health(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    return func.HttpResponse("Healthy!", status_code=200)


@app.route(route="trigger-check")
@app.durable_client_input(client_name="client")
async def http_trigger_function(req: func.HttpRequest, client):
    containers = [
        "hrdocuments/Current",
        "wcb-benefitsresourcecenter",
        "wcmc-benefitsresourcecenter",
        "wch-wca-wcm-wcw-wci-benefitsresourcecenter"
    ]

    instance_id = await client.start_new("orchestrator_function", None, containers)
    response = client.create_check_status_response(req, instance_id)

    return response


@app.route(route="trigger-check-all")
@app.durable_client_input(client_name="client")
async def http_trigger_function_all(req: func.HttpRequest, client):
    containers = [
        "hrdocuments/Current",
        "wcb-benefitsresourcecenter",
        "wcmc-benefitsresourcecenter",
        "wch-wca-wcm-wcw-wci-benefitsresourcecenter"
    ]

    instance_id = await client.start_new("orchestrator_function_all", None, containers)
    response = client.create_check_status_response(req, instance_id)

    return response


@app.orchestration_trigger(context_name="context")
def orchestrator_function(context: df.DurableOrchestrationContext):
    containers = context.get_input()
    records = context.call_activity("fetch_blob_metadata_activity", containers)
    tasks = [context.call_activity("process_activity", record) for record in records]
    yield context.task_all(tasks)

    return "Orchestration complete"


@app.orchestration_trigger(context_name="context")
def orchestrator_function_all(context: df.DurableOrchestrationContext):
    containers = context.get_input()
    records = yield context.call_activity("fetch_blob_metadata_activity_all", containers)
    for record in records:
        yield context.call_activity("process_activity", record)

    return "Orchestration complete"


@app.activity_trigger(input_name="containers")
def fetch_blob_metadata_activity(containers):
    return fetch_blob_metadata(containers)


@app.activity_trigger(input_name="containers")
def fetch_blob_metadata_activity_all(containers):
    return fetch_blob_metadata(containers, True)


@app.activity_trigger(input_name="record")
def process_activity(record):
    logging.info(f"Processing record: {record}")

    conn_string = os.getenv("AzureTriggerStorageConnection")
    AZURE_SEARCH_SERVICE_NAME = os.getenv('AZURE_SEARCH_SERVICE_NAME')
    AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
    AZURE_OPENAI_SERVICE = os.getenv('AZURE_OPENAI_SERVICE')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_API_VERSION = "2024-02-01"

    blob_service_client = BlobServiceClient.from_connection_string(conn_string)

    openai.api_type = "azure"
    openai.azure_endpoint = AZURE_OPENAI_SERVICE
    openai.api_version = AZURE_OPENAI_API_VERSION
    openai.api_key = AZURE_OPENAI_API_KEY

    parse_record(record, AZURE_SEARCH_SERVICE_NAME, AZURE_SEARCH_API_KEY, blob_service_client)
    return f"Processed record: {record['RowKey']}"


@app.blob_trigger(arg_name="blob", path="hrdocuments/Current/{name}", connection="AzureTriggerStorageConnection")
async def blob_trigger_function(blob: func.InputStream):
    await process_blob(blob, process_activity)


@app.blob_trigger(arg_name="blob", path="wcb-benefitsresourcecenter/{name}", connection="AzureTriggerStorageConnection")
async def blob_brc_wcb_trigger_function(blob: func.InputStream):
    await process_blob(blob, process_activity)


@app.blob_trigger(arg_name="blob", path="wcmc-benefitsresourcecenter/{name}", connection="AzureTriggerStorageConnection")
async def blob_brc_wcmc_trigger_function(blob: func.InputStream):
    await process_blob(blob, process_activity)


@app.blob_trigger(arg_name="blob", path="wch-wca-wcm-wcw-wci-benefitsresourcecenter/{name}", connection="AzureTriggerStorageConnection")
async def blob_brc_wch_trigger_function(blob: func.InputStream):
    await process_blob(blob, process_activity)
