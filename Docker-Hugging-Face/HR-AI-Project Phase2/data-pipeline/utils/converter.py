from datetime import datetime


def convert_to_serializable(record):
    for key, value in record.items():
        if isinstance(value, datetime):
            record[key] = value.isoformat()
    return record
