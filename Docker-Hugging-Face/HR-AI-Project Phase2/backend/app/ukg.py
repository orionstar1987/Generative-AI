import os
import requests


def get_pto(user_id: str):
    auth_token = os.getenv("WC_TOKEN")
    wc_api = os.getenv("WC_API")
    wc_test = os.getenv("WC_TEST") == "True"

    if wc_test:
        return {
            "error": False,
            "success": True,
            "employeeId": "test",
            "result": [
                {
                    "description": "PTO Vested Balance",
                    "value": "88.00"
                },
                {
                    "description": "Future Approved Time",
                    "value": "0.00"
                },
                {
                    "description": "Available PTO Balance",
                    "value": "88.00"
                }
            ]
        }

    if not auth_token:
        raise EnvironmentError("WC_TOKEN environment variable is not set")

    url = f"{wc_api}/soft-serve/pto-balances/{user_id}"

    headers = {
        "X-Auth-Token": auth_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
