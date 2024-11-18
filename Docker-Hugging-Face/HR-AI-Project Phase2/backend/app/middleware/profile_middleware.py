from flask import request, g
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import json
import requests

profile_cache = {}

def decode_jwt(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

def fetch_profile_from_graph(token):
    headers = {'Authorization': f'Bearer {token}'}
    graph_url = 'https://graph.microsoft.com/v1.0/me?$select=givenName,surname,mail,officeLocation,employeeId,department'
    response = requests.get(graph_url, headers=headers)
    if response.status_code == 200:
        response.json()
        return response.json()
    response.raise_for_status()

def profile_middleware():
    token = request.headers.get('x-profile-token')
    profile_info = request.headers.get('x-profile-info')
    profile_test = request.headers.get('x-profile-test')
    if profile_info:
        try:
            g.profile_info = json.loads(profile_info)
        except json.JSONDecodeError:
            g.profile_info = None
        return None

    if profile_test:
        try:
            g.profile_info = json.loads(profile_test)
        except json.JSONDecodeError:
            g.profile_info = None
        return None

    if not token:
        return None

    try:
        decoded_token = decode_jwt(token)
        email = decoded_token.get('email') or decoded_token.get('preferred_username')

        if not email:
            g.profile_info = None
            return

        if email in profile_cache:
            g.profile_info = profile_cache[email]
        else:
            data = fetch_profile_from_graph(token)
            if data:
                profile = {
                    "firstName": data["givenName"],
                    "lastName": data["surname"],
                    "email": data["mail"],
                    "property": data["officeLocation"],
                    "employeeId": data["employeeId"],
                    "department": data["department"]
                }
                profile_cache[email] = profile
                g.profile_info = profile
            else:
                raise ValueError("Invalid profile response")
    except ExpiredSignatureError:
        print("Token expired")
        g.profile_info = None
    except Exception as e:
        print(f"Error in profile middleware: {e}")
        g.profile_info = None
