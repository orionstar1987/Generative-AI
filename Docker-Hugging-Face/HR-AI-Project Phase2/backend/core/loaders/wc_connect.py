import os
import requests

from core.modules.base import Module
from typing import Any

from PIL import Image
import pytesseract
from io import BytesIO

def extract_text_from_image(image_url: str) -> str:
    # Download the image
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    # Perform OCR using Tesseract
    text = pytesseract.image_to_string(image)
    return text

def get_pto(user_id: str, wc_test: bool) -> dict[str, Any]:
    auth_token = os.getenv("WC_TOKEN")
    wc_api = os.getenv("WC_API")

    if wc_test:

        r = {'error': False,
             'success': True,
             'employeeId': 'test',
             'results': [
                 {'description': 'PTO Vested Balance', 'value': '59.00'},
                 {'description': 'Future Approved Time', 'value': '0.00'},
                 {'description': 'Available PTO Balance', 'value': '59.00'}]
             }

        return r

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


def get_scores(user_id: str, wc_test: bool) -> dict[str, Any]:
    auth_token = os.getenv("WC_TOKEN")
    wc_api = os.getenv("WC_API")
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


class ContextManager(Module):
    def __init__(self, test_mode: bool = False):
        super().__init__()
        self.test_mode = test_mode

    def invoke(self, user_id: str, categories: list[str]) -> str:
        return self.get_context(user_id, categories)

    def get_context(self, user_id: str, categories: list[str]) -> str:
        """
        Get context based on categories
        :param categories: list of context categories to be used. Empty list will return empty context
        :type categories: list[str]
        :return: formatted context string
        :rtype: str
        """
        print("Categories before mapping:", categories)
        if not categories:
            return ""
        if categories == 'nothing' or categories == ["nothing"]:
            return ""

        context = ""

        if 'Property_Scores' in categories:
            try:
                r = get_scores(user_id, wc_test=self.test_mode)
                print(f"Qualtrix raw respone: {r}")
                img_url = r.get('results')[0].get('image')
                scores = extract_text_from_image(img_url)
                mdate = get_scores(user_id, wc_test=self.test_mode).get('results')[0].get('dateModified')

                chunk = f"Here are the scores for the property as for {mdate}: /n{scores}"
                context += chunk
            except Exception as e:
                print(e)
                context += "Error occurred: Could not obtain property scores"

        if 'Leave_Questions' in categories:
            try:
                r = get_pto(user_id, wc_test=self.test_mode)
                print(f"UKG raw respone: {r}")
                result = r.get('results')
                result_formatted = self.list_of_dict_handler(result)
                chunk = f"Here is the balance of PTO hours for the user /n{result_formatted}"
                context += chunk
            except Exception as e:
                print(e)
                context += "Error occurred: Could not obtain PTO balance for the user"

        return context.strip()

    @staticmethod
    def dict_handler(arg: dict[str, str]) -> str:
        text = ""
        for k, v in arg.items():
            entry = f"{k}: {v}"
            text += f'{entry} \n'
        return text.strip()

    def list_of_dict_handler(self, arg: list[dict[str, str]]) -> str:
        text = ""
        for x in arg:
            text += self.dict_handler(x)
        return text

