from azure.data.tables import UpdateMode


def get_record(table_client, query: str):
    entities = table_client.query_entities(query_filter=query)
    results = []
    for entity in entities:
        results.append(entity)
    return results[0] if len(results) > 0 else None


def get_records(table_client):
    entities = table_client.list_entities()
    results = []
    for entity in entities:
        results.append(entity)

    return results


def update_last_processing(table_client, record, last_modified):
    record["LastProcessing"] = last_modified
    table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=record)
