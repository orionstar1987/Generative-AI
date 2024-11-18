import os
import requests


def get_scores(user_id: str):
    auth_token = os.getenv("WC_TOKEN")
    wc_api = os.getenv("WC_API")
    wc_test = os.getenv("WC_TEST") == "True"

    if wc_test:
        return {
            "success": True,
            "error": False,
            "employeeId": "test",
            "results": [
                {
                    "image": "https://web-dev.windcreekconnect.com/image.php?image=/img/scores/vog-62d84c573ce8c-sqc-5-9-22-(7w).jpg",
                    "dateModified": "07/20/2022"
                }
            ],
            "propertyCode": "pci"
        }

    if not auth_token:
        raise EnvironmentError("WC_TOKEN environment variable is not set")

    url = f"{wc_api}/soft-serve/voice-of-guests/{user_id}"

    headers = {
        "X-Auth-Token": auth_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
