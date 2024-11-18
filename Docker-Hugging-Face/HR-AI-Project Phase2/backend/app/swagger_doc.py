echo = {
    'response': {
        200: {
            'description': 'A successful response',
            'content': {
                'text/plain': {
                    'example': 'Hello, User!'
                }
            }
        }
    }
}

chat = {
    'tags': ['Chat'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authorization'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                '$ref': '#/definitions/ChatRequest'
            }
        }
    ],
    'definitions': {
        'ChatRequest': {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': 'User input message for the chatbot',
                    'example': 'Hello, how can I get started?'
                },
                'messageId': {
                    'type': 'string',
                    'description': 'Unique message identifier',
                    'example': '12345'
                },
                'sessionId': {
                    'type': 'string',
                    'description': 'Session identifier',
                    'example': 'abcde'
                },
                'regenerate': {
                    'type': 'boolean',
                    'description': 'Flag to regenerate the response',
                    'example': False
                }
            },
            'required': ['message', 'messageId', 'sessionId', 'regenerate']
        },
        'ChatResponse': {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': 'Response from the chatbot'
                },
                'messageId': {
                    'type': 'string',
                    'description': 'ID of the user’s message'
                },
                'sessionId': {
                    'type': 'string',
                    'description': 'Session identifier'
                }
            }
        }
    },
    'responses': {
        200: {
            'description': 'A successful response with the chatbot answer',
            'schema': {
                '$ref': '#/definitions/ChatResponse'
            },
            'examples': {
                'application/json': {
                    "message": "Chatbot response text",
                    "messageId": "12345",
                    "sessionId": "abcde"
                }
            }
        },
        400: {
            'description': 'Invalid request data or missing fields'
        },
        500: {
            'description': 'Internal server error'
        }
    }
}

feedback_post = {
    'tags': ['Feedback'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authorization'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                '$ref': '#/definitions/FeedbackRequest'
            }
        }
    ],
    'definitions': {
        'FeedbackRequest': {
            'type': 'object',
            'properties': {
                'messageId': {
                    'type': 'string',
                    'description': 'Unique identifier for the message being provided feedback on',
                    'example': 'bf4d04ef-8134-4c68-8dd7-ec10db80210a'
                },
                'isLiked': {
                    'type': 'boolean',
                    'description': 'Indicates if the user liked the chatbot response',
                    'example': True
                }
            },
            'required': ['messageId', 'isLiked']
        }
    },
    'responses': {
        200: {
            'description': 'Feedback submission was successful',
            'schema': {
                'type': 'string'
            },
            'examples': {
                'application/json': 'Ok'
            }
        },
        400: {
            'description': 'Invalid request data or missing fields'
        },
        500: {
            'description': 'Internal server error'
        }
    }
}

feedback_put = {
    'tags': ['Feedback'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authorization'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                '$ref': '#/definitions/FeedbackUpdateRequest'
            }
        }
    ],
    'definitions': {
        'FeedbackUpdateRequest': {
            'type': 'object',
            'properties': {
                'messageId': {
                    'type': 'string',
                    'description': 'Unique identifier for the message whose feedback is being updated',
                    'example': 'bf4d04ef-8134-4c68-8dd7-ec10db80210a'
                },
                'isLiked': {
                    'type': 'boolean',
                    'description': 'Updated feedback indicating if the user liked the chatbot response',
                    'example': False
                }
            },
            'required': ['messageId', 'isLiked']
        }
    },
    'responses': {
        200: {
            'description': 'Feedback update was successful',
            'schema': {
                'type': 'string'
            },
            'examples': {
                'application/json': 'Ok'
            }
        },
        400: {
            'description': 'Invalid request data or missing fields'
        },
        500: {
            'description': 'Internal server error'
        }
    }
}

session_post = {
    'tags': ['Session'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authorization'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                '$ref': '#/definitions/SessionRequest'
            }
        }
    ],
    'definitions': {
        'SessionRequest': {
            'type': 'object',
            'properties': {
                'sessionId': {
                    'type': 'string',
                    'description': 'Session identifier to create or retrieve session details',
                    'example': '68903ce1-b5cd-415e-b0c1-7a5a0698bc7c'
                }
            },
            'required': ['sessionId']
        },
        'SessionResponse': {
            'type': 'object',
            'properties': {
                'isAdmin': {
                    'type': 'boolean',
                    'description': 'Indicates if the user associated with the session has admin privileges',
                    'example': False
                },
                'sessionId': {
                    'type': 'string',
                    'description': 'Unique identifier for the session',
                    'example': '68903ce1-b5cd-415e-b0c1-7a5a0698bc7c'
                },
                'user': {
                    'type': 'string',
                    'description': 'Email address of the user associated with the session',
                    'example': 'iryba@softserveinc.com'
                }
            },
            'required': ['isAdmin', 'sessionId', 'user']
        }
    },
    'responses': {
        200: {
            'description': 'Session details retrieved successfully',
            'schema': {
                '$ref': '#/definitions/SessionResponse'
            },
            'examples': {
                'application/json': {
                    "isAdmin": False,
                    "sessionId": "68903ce1-b5cd-415e-b0c1-7a5a0698bc7c",
                    "user": "iryba@softserveinc.com"
                }
            }
        },
        400: {
            'description': 'Invalid request data or missing fields'
        },
        500: {
            'description': 'Internal server error'
        }
    }
}

session_get = {
    'tags': ['Session'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authorization'
        },
        {
            'name': 'sessionId',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Unique identifier for the session to retrieve messages',
            'example': '8fe6ff57-68b6-4539-b72b-46d4f18aa204'
        }
    ],
    'definitions': {
        'SessionMessage': {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': 'The content of the message',
                    'example': 'How is my tax calculated?'
                },
                'messageId': {
                    'type': 'string',
                    'description': 'Unique identifier for the message',
                    'example': '0b3e0ff6-0ffd-45f2-97f6-341f4e67867f'
                },
                'role': {
                    'type': 'string',
                    'description': 'The role of the message sender (e.g., "user" or "assistant")',
                    'example': 'user'
                },
                'sessionId': {
                    'type': 'string',
                    'description': 'Unique identifier for the session associated with the message',
                    'example': '8fe6ff57-68b6-4539-b72b-46d4f18aa204'
                }
            },
            'required': ['message', 'messageId', 'role', 'sessionId']
        }
    },
    'responses': {
        200: {
            'description': 'A list of messages associated with the specified session ID',
            'schema': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/SessionMessage'
                }
            },
            'examples': {
                'application/json': [
                    {
                        "message": "How is my tax calculated?",
                        "messageId": "0b3e0ff6-0ffd-45f2-97f6-341f4e67867f",
                        "role": "user",
                        "sessionId": "8fe6ff57-68b6-4539-b72b-46d4f18aa204"
                    },
                    {
                        "message": "I'm sorry, but I don't have specific information on how your taxes are calculated. Tax calculations can depend on various factors, including your income, tax withholdings, and any applicable deductions or credits. For detailed information about your tax calculations, I recommend contacting your HR department or a tax professional who can provide guidance based on your specific situation. If you have any other questions or need further assistance, please let me know.",
                        "messageId": "0b3e0ff6-0ffd-45f2-97f6-341f4e67867f",
                        "role": "assistant",
                        "sessionId": "8fe6ff57-68b6-4539-b72b-46d4f18aa204"
                    }
                ]
            }
        },
        400: {
            'description': 'Invalid session ID or request data'
        },
        404: {
            'description': 'Session not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
}

recent = {
    'tags': ['Recent'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authorization'
        }
    ],
    'definitions': {
        'RecentResponseItem': {
            'type': 'object',
            'properties': {
                'CreatedOnUtc': {
                    'type': 'string',
                    'format': 'date-time',
                    'description': 'The UTC timestamp when the record was created',
                    'example': 'Fri, 15 Nov 2024 08:11:52 GMT'
                },
                'Question': {
                    'type': 'string',
                    'description': 'The question or message asked by the user',
                    'example': 'Hi'
                },
                'SessionId': {
                    'type': 'string',
                    'description': 'Unique identifier for the session associated with the record',
                    'example': 'c7bcc1a1-51ed-4fb0-bb83-f9ca2ee29eb4'
                }
            },
            'required': ['CreatedOnUtc', 'Question', 'SessionId']
        }
    },
    'responses': {
        200: {
            'description': 'A list of recent records',
            'schema': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/RecentResponseItem'
                }
            },
            'examples': {
                'application/json': [
                    {
                        "CreatedOnUtc": "Fri, 15 Nov 2024 08:11:52 GMT",
                        "Question": "Hi",
                        "SessionId": "c7bcc1a1-51ed-4fb0-bb83-f9ca2ee29eb4"
                    }
                ]
            }
        },
        400: {
            'description': 'Invalid request'
        },
        500: {
            'description': 'Internal server error'
        }
    }
}

document = {
    'tags': ['Document'],
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authorization'
        },
        {
            'name': 'url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'URL of the document to retrieve',
            'example': 'https://wchesstghrai01.blob.core.windows.net/hrdocuments/Current/Benefits/Benefits%20Guide.pdf'
        }
    ],
    'responses': {
        200: {
            'description': 'A PDF document retrieved successfully',
            'schema': {
                'type': 'file'
            },
            'examples': {
                'application/pdf': 'Binary data of the PDF file'
            }
        },
        400: {
            'description': 'Invalid URL or request parameters'
        },
        404: {
            'description': 'Document not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
}
