"""Config for Flask injector"""

import os
import json
from logging import Logger, getLogger
from injector import singleton, Binder
from opentelemetry import trace
from opentelemetry.trace import Tracer

from .dataaccess import DBAccess, DataAccess
from .bootstrap import FlowManager
from .logger import AppLogger


class Config:
    """Configuration class"""

    @staticmethod
    def configure(binder: Binder) -> None:
        """Configuration for dependency injection"""

        CHATACTIVITY_DB_CONNECTIONSTRING = os.getenv("CHATACTIVITY_DB_CONNECTIONSTRING")
        COMPONENT_NAME = "WCH-HRAI-API"
        LOGGING_ENABLED = json.loads((os.getenv("LOGGING_ENABLED") or "true").lower())
        APPINSIGHTS_CONNECTION_STRING = os.getenv(
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        )

        flow_manager = FlowManager
        binder.bind(FlowManager, to=flow_manager, scope=singleton)
        logger = getLogger(COMPONENT_NAME)
        tracer = trace.get_tracer(COMPONENT_NAME)

        if LOGGING_ENABLED:
            app_logger = AppLogger(
                config={
                    "logging_enabled": "true" if LOGGING_ENABLED else "false",
                    "log_level": "INFO",
                    "app_insights_connectionstring": APPINSIGHTS_CONNECTION_STRING,
                }
            )
            logger = app_logger.get_logger(component_name=COMPONENT_NAME)
            tracer = app_logger.get_tracer(component_name=COMPONENT_NAME)
        binder.bind(Logger, to=logger, scope=singleton)
        binder.bind(Tracer, to=tracer, scope=singleton)
        binder.bind(
            DBAccess,
            to=DataAccess(CHATACTIVITY_DB_CONNECTIONSTRING, logger),
            scope=singleton,
        )
