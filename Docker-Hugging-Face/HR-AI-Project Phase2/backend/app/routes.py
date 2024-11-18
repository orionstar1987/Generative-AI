"""This is backend flask api
"""

import contextlib
import json
import re
import os
import asyncio
import io

from logging import Logger

from flask import current_app as app, jsonify, request, g, send_file
from flask_injector import inject
from opentelemetry.trace import Tracer
from azure.storage.blob import BlobServiceClient
from flasgger import swag_from

from .bootstrap import ConversationFlow, FlowManager
from .dataaccess import DBAccess
from .middleware.middleware import token_required
from .middleware.profile_middleware import profile_middleware
from .swagger_doc import echo, chat, feedback_post, feedback_put, session_post, recent, session_get, document

blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_STORAGE_CONN_STRING'))


@app.before_request
def get_profile_info():
    profile_middleware()


@app.errorhandler(Exception)
@inject
def handle_global_exception(error, logger: Logger):
    """Handles global exceptions not handled by any function or decorator

    Args:
        error (obj): exception or error object

    Returns:
        obj: returns 500 error resposne for clients
    """
    if logger is not None:
        logger.exception(f"Exception occurred. {error}")
    response = {"error": str(error), "message": "A global error occurred."}
    return jsonify(response), 500


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    """Serve static files from the 'static' directory"""
    return app.send_static_file(path)


@app.route("/api/echo", methods=["GET"])
@swag_from(echo)
@token_required
def echo():
    """This is an echo api.

    Returns:
        str: Returns 'ok' if there is no exception
    """
    return jsonify("OK")


@app.route("/api/chat", methods=["POST"])
@swag_from(chat)
@token_required
@inject
def chat(dbaccess: DBAccess, flow_manager: FlowManager, logger: Logger, tracer: Tracer):
    """This is a chat api. process the users input.

    Returns:
        str: Returns response from LLM if there is no exception
    """
    with (
        tracer.start_as_current_span("api/chat")
        if tracer is not None
        else contextlib.nullcontext()
    ):
        user_input = request.json["message"]
        message_id = request.json["messageId"]
        session_id = request.json["sessionId"]
        regenerate = request.json["regenerate"]

        # get values from middleware
        property_idx = g.get("profile_info", {}).get("property") or 'null'
        user_id = g.get("profile_info", {}).get("employeeId") or 'null'

        conversation_flow = flow_manager.get(user_id, session_id)

        answer = asyncio.run(conversation_flow.invoke(user_message=user_input, property_idx=property_idx, user_id=user_id))
        topics = conversation_flow.classification.get('Topics', ['None'])

        if not regenerate:
            dbaccess.add_userinteraction(
                message_id,
                session_id,
                user_input,
                answer,
                topics
            )
        else:
            dbaccess.update_userinteraction(message_id, answer)
    return {
        "message": answer,
        "messageId": message_id,
        "sessionId": session_id,
    }


@app.route("/api/feedback", methods=["post"])
@swag_from(feedback_post)
@token_required
@inject
def add_userfeedback(dbaccess: DBAccess):
    """This is an api to add user feedback

    Returns:
        str: Returns 'ok' if there is no exception
    """

    message_id = request.json["messageId"]
    is_liked = request.json["isLiked"]
    dbaccess.add_userinteractionfeedback(message_id, is_liked)
    return jsonify("Ok")


@app.route("/api/feedback", methods=["put"])
@swag_from(feedback_put)
@token_required
@inject
def update_userfeedback(dbaccess: DBAccess):
    """This is an api to update user feedback

    Returns:
        str: Returns 'ok' if there is no exception
    """
    message_id = request.json["messageId"]
    is_liked = request.json["isLiked"]
    dbaccess.update_userinteractionfeedback(message_id, is_liked)
    return jsonify("Ok")


@app.route("/api/session", methods=["post"])
@swag_from(session_post)
@token_required
@inject
def add_usersession(dbaccess: DBAccess):
    """This is an api to log user login entry

    Returns:
        str: Returns 'ok' if there is no exception
    """

    login_user = g.get("profile_info")["email"]

    session_id = request.json["sessionId"]
    property_value = g.get("profile_info", {}).get("property")
    department = g.get("profile_info", {}).get("department")
    dbaccess.add_usersession(session_id, login_user, property_value, department)
    admin_users =  os.getenv('ADMIN_USERS', '').split(';')
    return jsonify({"sessionId": session_id, "user": login_user, 'isAdmin': any(s.lower() == login_user.lower() for s in admin_users)})


@app.route("/api/recent", methods=["get"])
@swag_from(recent)
@token_required
@inject
def recent(dbaccess: DBAccess):
    """get recents sessions

    Returns:
        list: list top 20 recent sessions
    """
    result = dbaccess.get_usersessions(g.get("profile_info")["email"])

    return jsonify(result)


@app.route("/api/session/<session_id>", methods=["get"])
@swag_from(session_get)
@token_required
@inject
def get_session(dbaccess: DBAccess, session_id):
    """Get session information

    Args:
        session_id (str): session id

    Returns:
        list: returns list of user interactions related to the session
    """

    result = dbaccess.get_userinteractions(session_id)
    messages = []
    for row in result:
        messages.append(
            {
                "messageId": row["UserInteractionId"],
                "sessionId": row["UserSessionId"],
                "message": row["Question"],
                "role": "user",
            }
        )
        messages.append(
            {
                "messageId": row["UserInteractionId"],
                "sessionId": row["UserSessionId"],
                "message": row["Answer"],
                "role": "assistant",
            }
        )
    return jsonify(messages)


@app.route('/api/document', methods=['GET'])
@swag_from(document)
@token_required
def download_document():
    document_url = request.args.get('url')
    if not document_url:
        return jsonify({"error": "Missing document URL"}), 400

    try:
        path_parts = document_url.split('.blob.core.windows.net/')[-1].split('/')
        container_name = path_parts[0]
        blob_name = '/'.join(path_parts[1:])

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name="document.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to retrieve document from Blob Storage"}), 500


@app.route('/api/submit-feedback', methods=['POST'])
@token_required
@inject
def submit_feedback(dbaccess: DBAccess):
    data = request.get_json()
    feedback_text = data.get('feedback')
    screenshot = data.get('screenshot')
    email = g.get("profile_info", {}).get("email")
    property_value = g.get("profile_info", {}).get("property")

    dbaccess.add_userfeedback(feedback_text, screenshot, email, property_value)

    return jsonify({"message": "Feedback submitted successfully!"}), 201


def _clean_json_string(json_string):
    pattern = r"^```json\s*(.*?)\s*```$"
    cleaned_string = re.sub(pattern, r"\1", json_string, flags=re.DOTALL)
    return cleaned_string.strip()
