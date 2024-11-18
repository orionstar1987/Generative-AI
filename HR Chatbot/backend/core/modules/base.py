from abc import ABCMeta, abstractmethod
# from snowflake.connector import connect, SnowflakeConnection
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
import os
from functools import wraps
from typing import Any, Dict


class Module(metaclass=ABCMeta):
    """Template class for LLM flow modules"""
    def __init__(self):
        ...

    @abstractmethod
    def invoke(self, *args, **kwargs):
        ...

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

# class SnowflakeModule(metaclass=ABCMeta):
#     """
#     Template for modules that require Snowflake connection.
#
#     Usage:
#     Before initialization set environment variables to define Snowflake connection:
#     SNOWFLAKE_PASSWORD <string>: password to selected SF user account. Mandatory
#     SNOWFLAKE_ACCOUNT <string>: Snowflake Account ID
#     SNOWFLAKE_USER <string>: Snowflake User
#     SNOWFLAKE_DB <string>: default Snowflake database
#     SNOWFLAKE_SCHEMA <string>: default Snowflake schema
#     SNOWFLAKE_WH <string>: Snowflake compute warehouse
#     SNOWFLAKE_ROLE <string>: Snowflake role with access to selected schemas
#     SNOWFLAKE_REGION <string> AWS region for Snowflake instance
#
#     Class will provide connection attribute for child classes
#     To wrap a method of a child class in Snowflake connection - use @snowflake decorator in method definition.
#     You can use active self.connection attribute inside that that class to connect to Snowflake.
#     Connection will be terminated on wrapped method return
#     """
#     def __init__(self):
#         self.connection: SnowflakeConnection
#
#         self.account = os.getenv('SNOWFLAKE_ACCOUNT')
#         self.user = os.getenv('SNOWFLAKE_USER')
#         self.database = os.getenv('SNOWFLAKE_DB')
#         self.schema = os.getenv('SNOWFLAKE_SCHEMA')
#         self.warehouse = os.getenv('SNOWFLAKE_WH')
#         self.role = os.getenv('SNOWFLAKE_ROLE')
#         self.region = os.getenv('SNOWFLAKE_REGION')
#         self.password = os.getenv('SNOWFLAKE_PASSWORD')
#
#     def _connect(self):
#         self.connection = connect(account=self.account,
#                                   user=self.user,
#                                   password=self.password,
#                                   database=self.database,
#                                   schema=self.schema,
#                                   warehouse=self.warehouse,
#                                   role=self.role,
#                                   region=self.region)
#
#     def _diconnect(self):
#         self.connection.close()
#
#     @staticmethod
#     def snowflake(func):
#         @wraps(func)
#         def wrapped(inst, *args, **kwargs):
#             inst._connect()
#             r = func(inst, *args, **kwargs)
#             inst._diconnect()
#             return r
#         return wrapped


class Memory(metaclass=ABCMeta):
    """Langchain-compatible memory template"""
    def __init__(self, size: int, ai_role: str = 'Assistant', human_role: str = 'User', return_messages: bool = False):
        self.size = size
        self.ai_role = ai_role
        self.human_role = human_role
        self.return_messages = return_messages

    @abstractmethod
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return message history

        :param inputs: dictionary of additional inputs append to history (last step). Pass empty dict to get only
        buffered history
        :type inputs: Dict[str, Any]
        """
        pass

    @abstractmethod
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Save new messages to memory buffer
        :param inputs: dictionary of input messages. One of them must have user role
        :type inputs: Dict[str, Any]
        :param outputs: dictionary of output messages. One of them must have assistant role
        :type outputs: Dict[str, Any]
        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear memory"""
        pass

    def _msg_to_str(self, inputs: Dict[str, Any]) -> str:
        return f"{self.human_role}: {inputs.get(self.human_role)}\n{self.ai_role}: {inputs.get(self.ai_role)}\n"

    def _msg_to_msg(self, inputs: Dict[str, Any]) -> tuple[BaseMessage, BaseMessage]:
        human_message = HumanMessage(content=inputs.get(self.human_role))
        ai_message = AIMessage(content=inputs.get(self.ai_role))
        return human_message, ai_message

    