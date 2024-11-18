import json
import os
import requests
import jwt
from jwt.algorithms import RSAAlgorithm
from functools import wraps
from flask import Flask, request, jsonify
import base64
import time

app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
TENANT_ID = os.getenv('TENANT_ID')
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"

cached_keys = None
keys_last_updated = 0
cache_duration = 60 * 60

clients = {
    "client_1": "client_1"
}


def get_openid_config():
    try:
        openid_config_url = f"{ISSUER}/.well-known/openid-configuration"
        response = requests.get(openid_config_url)
        return response.json()
    except Exception as e:
        print(f"Error fetching OpenID config: {e}")
        return None


def get_public_keys():
    global cached_keys, keys_last_updated

    if cached_keys and (time.time() - keys_last_updated < cache_duration):
        return cached_keys

    jwks_uri = get_openid_config().get("jwks_uri")
    if jwks_uri:
        response = requests.get(jwks_uri)
        jwks = response.json()
        cached_keys = {key['kid']: key for key in jwks['keys']}
        keys_last_updated = time.time()
        return cached_keys
    return None


def decode_base64(base64_string):
    decoded_bytes = base64.b64decode(base64_string)
    return decoded_bytes.decode("utf-8")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get('x-auth-token')
        if auth_token:
            try:
                cred_decoded = decode_base64(auth_token)
                client_id, client_secret = cred_decoded.split(":")
                if client_id not in clients or clients[client_id] != client_secret:
                    return jsonify({"error": "Invalid token key"}), 401
                profile_info = request.headers.get('x-profile-info')
                if not profile_info:
                    return jsonify({"error": "The server to server authorization requires profile info in the 'X-Profile-Info' header"}), 400
            except Exception:
                return jsonify({"error": "Invalid token key"}), 401
        else:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "Authorization header missing"}), 401

            try:
                token = auth_header.split(" ")[1]

                keys = get_public_keys()
                if not keys:
                    return jsonify({"error": "Unable to fetch public keys"}), 500

                unverified_header = jwt.get_unverified_header(token)
                rsa_key = keys.get(unverified_header["kid"])

                if rsa_key:
                    public_key = RSAAlgorithm.from_jwk(json.dumps(rsa_key))

                    decoded_token = jwt.decode(
                        token,
                        public_key,
                        algorithms=["RS256"],
                        audience=CLIENT_ID,
                        issuer=ISSUER
                    )

                    request.decoded_token = decoded_token
                else:
                    return jsonify({"error": "Invalid token key"}), 401

            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError as e:
                return jsonify({"error": f"Invalid token: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated
