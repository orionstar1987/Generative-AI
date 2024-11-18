from operator import itemgetter

from typing import Any, Union

from langchain.memory.chat_memory import BaseChatMemory
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from core.modules.base import Memory, Module
import re


class QuestionRecommender(Module):
    """
    Module for recommendation of standalone questions like clarification
    """
    def __init__(self, llm: AzureChatOpenAI,
                 template: str,
                 user_context_prompt: str,
                 rag_prompt: str,
                 system_prompt: str = None,
                 **kwargs
                 ):
        """
        :param llm: langchain AzureChatOpenAI instance
        :type llm: langchain_openai.AzureChatOpenAI
        :param template: clarification question prompt template with <<<aux_context_prompt>>>, <<<rag_prompt>>> and
         {user_message} placeholders
        :type template: str
        :param user_context_prompt: personal context template with {aux_context} placeholder
        :type user_context_prompt: str
        :param rag_prompt: RAG context template with {rag_context} placeholder
        :type rag_prompt: str
        :param system_prompt: system prompt for the task
        :type system_prompt: str
        :param kwargs: kwargs placeholder, added for compatibility
        :type kwargs: Any
        """
        super().__init__()
        self.template = template
        self.user_context_prompt = user_context_prompt
        self.rag_prompt = rag_prompt
        self.llm = llm
        self.system_prompt = system_prompt

    def invoke(self, user_message: str,
                   user_context: str,
                   rag_context: str,
                   memory: Union[BaseChatMemory, Memory]) -> tuple[bool, list[str]]:
        """
        Get standalone question recommendation based on user message, context and conversation history
        :param user_message: Current user message (plain text)
        :type user_message: str
        :param user_context: Personal user context (plain text)
        :type user_context: str
        :param rag_context: Context retrieved from vector search (plain text)
        :type rag_context: str
        :param memory: Langchain-style memory for current conversation flow
        :type memory: langchain.memory.chat_memory.BaseChatMemory | core.base.Memory
        :return: tuple of two elements:
        r[0]: flag marking if clarification question is required
        r[1]: list of recommended questions in plain text (empty if flag is False)
        :rtype: tuple[bool, list[str]]
        """
        print(f"User Message: {user_message} \nUser Context: {user_context}")

        if rag_context:
            return self.rag_invoke(user_message, user_context, rag_context, memory)

        if user_context:
            human_message_template = self.template.replace('<<<user_context_prompt>>>', self.user_context_prompt)
        else:
            human_message_template = self.template.replace('<<<user_context_prompt>>>', '')

        human_message_template = human_message_template.replace('<<<rag_prompt>>>', '')

        chat_answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=self.system_prompt
            ),
            MessagesPlaceholder(
                variable_name="history"
            ),
            HumanMessagePromptTemplate.from_template(
                human_message_template
            ),
        ])

        memory.load_memory_variables({})
        answer_chain = (
                    RunnablePassthrough.assign(
                        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
                    )
                    | chat_answer_prompt
                    | self.llm
                    )

        if user_context:
            response = answer_chain.invoke({"user_context": user_context,
                                        "user_message": user_message,
                                        "rag_context": rag_context})
        else:
            response = answer_chain.invoke({"user_message": user_message,
                                        "rag_context": rag_context})

        return self.parse_response(response)

    def rag_invoke(self, user_message: str,
                   user_context: str,
                   rag_context: str,
                   memory: Union[BaseChatMemory, Memory]) -> tuple[bool, list[str]]:
        """
        Get standalone question recommendation based on user message, context and conversation history if RAG context
        is provided. This can be used as standalone method, but it's advised to let self.invoke() methode handle
        control flow.

        :param user_message: Current user message (plain text)
        :type user_message: str
        :param user_context: Personal user context (plain text)
        :type user_context: str
        :param rag_context: Context retrieved from vector search (plain text)
        :type rag_context: str
        :param memory: Langchain-style memory for current conversation flow
        :type memory: langchain.memory.chat_memory.BaseChatMemory | core.base.Memory
        :return: tuple of two elements:
        r[0]: flag marking if clarification question is required
        r[1]: list of recommended questions in plain text (empty if flag is False)
        :rtype: tuple[bool, list[str]]
        """
        print(f"User Message: {user_message} \nUser Context: {user_context}")

        if user_context:
            human_message_template = self.template.replace('<<<user_context_prompt>>>', self.user_context_prompt)
        else:
            human_message_template = self.template.replace('<<<user_context_prompt>>>', '')

        human_message_template = human_message_template.replace('<<<rag_prompt>>>', self.rag_prompt)

        chat_answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=self.system_prompt
            ),
            MessagesPlaceholder(
                variable_name="history"
            ),
            HumanMessagePromptTemplate.from_template(
                human_message_template
            ),
        ])

        memory.load_memory_variables({})
        answer_chain = (
                    RunnablePassthrough.assign(
                        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
                    )
                    | chat_answer_prompt
                    | self.llm
                    )

        if user_context:
            response = answer_chain.invoke({"user_context": user_context,
                                        "user_message": user_message,
                                        "rag_context": rag_context})
        else:
            response = answer_chain.invoke({"user_message": user_message,
                                        "rag_context": rag_context})

        return self.parse_response(response)

    @staticmethod
    def parse_response(res) -> tuple[bool, list[str]]:
        """
        Parse response from LLM. You may need to adjust this function when output formatting of LLM is altered.
        :param res: Runnable output
        :type res: langchain_core.runnables.utils.Output
        :return: tuple of two elements:
        r[0]: flag marking if clarification question is required
        r[1]: parsed list of recommended questions in plain text (empty if flag is False)
        :rtype: tuple[bool, list[str]]
        """
        # noinspection RegExpDuplicateCharacterInClass
        rx = re.compile(r"(?<!,)[^[,\[]+(?=[,\]][^,\[]*)")
        rx2 = re.compile(r'"(.*?)"')
        try:
            print(f'Raw response: {res.content}')
            items = re.findall(rx, res.content)
            flag = items[0].lower().strip() == 'true'
            questions = [x.strip() for x in re.findall(rx2, res.content)]
            print(flag, questions)

            return flag, questions

        except Exception as e:
            print("Error parsing chat output:")
            print(e)
            print("Classifier output:", res.content)
            return False, []

