def get_blob_url(account_name: str, blob_name: str) -> str:
    return f"https://{account_name}.blob.core.windows.net/hrdocuments/Current/{blob_name}"