from operator import itemgetter
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder)
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import AzureChatOpenAI
from typing import Any,  Callable, Union
from .base import Module, Memory
from core.templates.classification import user_message_template

class LLMBaseClassifier(Module):
    """
    Base LLM multilabel classifier
    """
    def __init__(self, llm: Any,
                 template: str,
                 categories: dict[str, str] = None,
                 replacement_dict: dict[str, Any] = None,
                 system_prompt: str = None,
                 custom_handlers: dict[str, Callable] = None,
                 response_parser: Callable = None):

        if not categories and replacement_dict is None:
            raise ValueError('categories or replacement_dict must be provided')

        self.categories = categories

        if replacement_dict is None:
            replacement_dict = {'categories': categories}

        super().__init__()
        if not custom_handlers:
            custom_handlers = dict()

        for item in replacement_dict:
            replacement_raw = replacement_dict.get(item)
            handler = custom_handlers.get(item, self._get_default_handler(replacement_raw))
            replacement = handler(replacement_raw)
            template = template.replace(f'<<<{item.lower()}>>>', replacement)
        if system_prompt:
            template = system_prompt + '/n' + template

        self.prompt = template
        self.llm = llm
        self.response_parser = response_parser

    @staticmethod
    def list_handler(arg: list) -> str:
        return ', '.join(arg).strip()

    @staticmethod
    def dict_handler(arg: dict[str, str]) -> str:
        text = ""
        for k, v in arg.items():
            entry = f"{k}: {v}"
            text += f'{entry} \n'
        return text.strip()

    @staticmethod
    def identity(arg: Any) -> Any:
        return arg

    def _get_default_handler(self, arg: Any) -> Callable:
        if isinstance(arg, (list, tuple)):
            return self.list_handler
        if isinstance(arg, dict):
            return self.dict_handler
        return self.identity


class LLMClassifierAzure(LLMBaseClassifier):
    """
    Azure OpenAI based LLM classifier
    """
    def __init__(self, llm: AzureChatOpenAI,
                 template: str,
                 categories: dict[str, str] = None,
                 replacement_dict: dict[str, Any] = None,
                 system_prompt: str = None,
                 custom_handlers: dict[str, Callable] = None,
                 response_parser: Callable = None,
                 ):
        """
        :param llm: langchain AzureChatOpenAI client
        :type llm: langchain_openai.AzureChatOpenAI
        :param template: classification templates, with placeholders wrapped in <<<>>> (default: <<<categories>>>)
        :type template: str
        :param categories: dictionary of categories in format {category_name: category_description, ...}.
        This will be used to replace default <<<categories>>> placeholder in template if replacement_dict is not provided
        :type categories: dict[str, str]
        :param replacement_dict: dictionary of items to be replaced in format {placeholder_1: values_1,...}.
        All placeholders present in template should be covered by replacement_dict.
        If only <<<categories>> placeholder is used - use categories instead.
        Default handlers for values in dict are implemented for list, dict (not nested) and primitives: str, int, float
        :type replacement_dict: dict[str, Any]
        :param system_prompt: system prompt for the task
        :type system_prompt: str
        :param custom_handlers: dictionary of handler functions f(x: Any) -> str for parsing structures
        in replacement_dict not handled by default. Format expected: {placeholder_1: f_1(x),...}.
        When using custom_handlers handler must be explicitly provided for each item in replacement_dict
        :type custom_handlers: dict[str, Callable]
        :param response_parser: function to parse LLM response, f(x: Any) -> str
        :type response_parser: Callable
        """
        if response_parser is None:
            response_parser = self.parse_response

        super().__init__(llm, template,
                         categories=categories,
                         replacement_dict=replacement_dict,
                         system_prompt=system_prompt,
                         custom_handlers=custom_handlers,
                         response_parser=response_parser)

        print(self.prompt)

    def invoke(self, user_message: str) -> list[str]:
        messages = [
                SystemMessage(content=self.prompt),
                HumanMessage(content=user_message)
            ]

        response = self.llm.invoke(messages)

        return self.response_parser(response)

    def invoke_with_memory(self, user_message: str,
                           memory: Union[BaseChatMemory, Memory],
                           user_message_template: str = user_message_template) -> list[str]:

        messages = ChatPromptTemplate.from_messages([
                SystemMessage(content=self.prompt),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template(user_message_template)
            ])

        memory.load_memory_variables({})

        answer_chain = (
                RunnablePassthrough.assign(
                    history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
                )
                | messages
                | self.llm
        )
        response = answer_chain.invoke({"query": user_message})

        return self.response_parser(response)


    @staticmethod
    def parse_response(res) -> list[str]:
        try:
            rtext = res.content
            print(f'Raw response: {rtext}')
            items = rtext.replace('[', '').\
                    replace(']', '').\
                    replace('"', '').\
                    replace("'", '').\
                    split(',')
            return [x.strip() for x in items]

        except Exception as e:
            print("Error parsing chat output:")
            print(e)
            print("Classifier output:", res.content)
            return []