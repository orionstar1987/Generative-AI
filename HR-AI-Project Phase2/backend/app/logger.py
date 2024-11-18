"""Helper classs for handling logging"""

import os
import logging
import uuid
from os import getenv

# pylint: disable=no-name-in-module
from azure.monitor.opentelemetry.exporter import (
    ApplicationInsightsSampler,
    AzureMonitorLogExporter,
    AzureMonitorTraceExporter,
)

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


class CustomDimensionsFilter(logging.Filter):
    """Add custom-dimensions in each log by using filters."""

    def __init__(self, component_name="AppLogger", custom_dimensions=None):
        """Initialize CustomDimensionsFilter."""

        super().__init__(name=component_name)

        self.custom_dimensions = (
            custom_dimensions if custom_dimensions is not None else {}
        )

    def filter(self, record):
        """Add the default custom_dimensions into the current log record."""
        dim = {**self.custom_dimensions, **getattr(record, "custom_dimensions", {})}
        record.custom_dimensions = dim
        return True


class AppLogger:
    """Logger wrapper that attach the handler to Application Insights."""

    HANDLER_NAME = "Azure Application Insights Handler"

    EVENT_HANDLER_NAME = "Azure Application Insights Event Handler"
    APPINSIGHTS_CONNECTION_STRING = "APPLICATIONINSIGHTS_CONNECTION_STRING"

    def __init__(self, config=None):
        """Create an instance of the Logger class.

        Args:
            config:([dict], optional):
                Contains the setting for logger {"log_level": "DEBUG","logging_enabled":"true"",
                "app_insights_connectionstring":"<app insights connection string>"}
        """
        self.config = {"log_level": logging.INFO, "logging_enabled": "true"}
        self.app_insights_connectionstring = None
        self.update_config(config)

    def _initialize_azure_log_handler(self, component_name, custom_dimensions):
        """Initialize azure log handler."""
        logger_provider = LoggerProvider()
        set_logger_provider(logger_provider)

        exporter = AzureMonitorLogExporter(
            connection_string=self._get_app_insights_connectionstring()
        )

        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        log_handler = LoggingHandler()
        log_handler.name = self.HANDLER_NAME
        log_handler.addFilter(CustomDimensionsFilter(component_name, custom_dimensions))
        return log_handler

    def _get_trace_exporter(self, sampler):
        """[Get log exporter]

        Returns:
            [AzureExporter]: [Azure Trace Exporter]
        """

        tracer_provider = TracerProvider(sampler=sampler)
        trace.set_tracer_provider(tracer_provider)
        # This is the exporter that sends data to Application Insights
        exporter = AzureMonitorTraceExporter(
            connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
        )
        span_processor = BatchSpanProcessor(exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        return exporter

    def _initialize_logger(self, log_handler, component_name):
        """Initialize Logger."""
        logger = logging.getLogger(component_name)
        logger.setLevel(self.log_level)
        if self.config.get("logging_enabled") == "true":
            if not any(
                x
                for x in logger.handlers
                if x.name in (self.HANDLER_NAME, self.EVENT_HANDLER_NAME)
            ):
                logger.addHandler(log_handler)
        return logger

    def get_logger(self, component_name="AppLogger", custom_dimensions=None):
        """Get Logger Object.

        Args:
            component_name (str, optional): Name of logger. Defaults to "AppLogger".
            custom_dimensions (dict, optional): {"key":"value"} to capture with every log.
                Defaults to {}.

        Returns:
            Logger: A logger.
        """
        self.update_config(self.config)

        if custom_dimensions is None:
            custom_dimensions = {}
        handler = self._initialize_azure_log_handler(component_name, custom_dimensions)
        return self._initialize_logger(handler, component_name)

    def get_tracer(self, component_name="AppLogger"):
        """Get Tracer Object."""
        self.update_config(self.config)
        sampler = ApplicationInsightsSampler(1)

        if self.config.get("logging_enabled") != "true":
            sampler = ApplicationInsightsSampler(0)

        self._get_trace_exporter(sampler)
        tracer = trace.get_tracer(component_name)
        return tracer

    @staticmethod
    def enable_flask(flask_app):
        """Enable flask for tracing

        Args:
            flask_app ([type]): [description]
        """
        FlaskInstrumentor().instrument_app(flask_app)
        RequestsInstrumentor().instrument()

    def _get_app_insights_connectionstring(self):
        """Get Application Insights connection string."""
        if self.app_insights_connectionstring is None:
            self.app_insights_connectionstring = getenv(
                self.APPINSIGHTS_CONNECTION_STRING, None
            )
        if self.app_insights_connectionstring is not None:
            # utils.validate_instrumentation_key(self.app_insights_connectionstring)
            return self.app_insights_connectionstring

        raise ValueError("ApplicationInsights Connection string is not set")

    def update_config(self, config=None):
        """Update logger configuration."""
        if config is not None:
            self.config.update(config)
        self.app_insights_connectionstring = self.config.get(
            "app_insights_connectionstring"
        )
        self.log_level = self.config.get("log_level")


def get_disabled_logger():
    """Get a disabled AppLogger.

    Returns:
        AppLogger: A disabled AppLogger
    """
    return AppLogger(
        config={
            "logging_enabled": "false",
            "app_insights_connectionstring": f"InstrumentationKey={str(uuid.uuid1())}",
        }
    )
