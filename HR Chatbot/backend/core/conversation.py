from operator import itemgetter
from typing import Union

from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from core.modules.base import Memory
from core.modules.classifier import LLMClassifierAzure
from core.modules.retriever import IndexManager
from core.modules.state import ConversationState
from core.modules.clarification import QuestionRecommender
from core.modules.utils import Translator
from core import templates
from core.templates.context import rag_query_prompt
from core.templates.faq import faq_query_template, faq_system_message
from core.loaders.mappings import topic_to_rag_mapping, topic_mapping
from core.loaders.wc_connect import ContextManager


class HRBot:
    """
    Interface for getting final LLM answers
    """
    def __init__(self, chat_answer: BaseChatModel, chat_standalone: BaseChatModel):
        """

        :param chat_answer: chat model for questions with context
        :type chat_answer: langchain_core.language_models.BaseChatModel
        :param chat_standalone: chat model for questions without additional context
        :type chat_standalone:langchain_core.language_models.BaseChatModel
        """
        self.chat_answer = chat_answer
        self.chat_standalone = chat_standalone

    def invoke(self, user_message: str, system_message: str, aux_context: str, memory: Union[BaseChatMemory, Memory]):

        system_prompt = system_message
        print(f"User Message: {user_message} \nAuxiliary Context: {aux_context}")
        if aux_context:
            human_message_template = templates.human_message_template_with_context
            chat = self.chat_answer
        else:
            human_message_template = templates.human_message_template_without_context
            chat = self.chat_standalone

        chat_answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=system_prompt
            ),
            MessagesPlaceholder(
                variable_name="history"
            ),
            HumanMessagePromptTemplate.from_template(
                human_message_template
            ),
        ])

        print(memory.load_memory_variables({}))
        answer_chain = (RunnablePassthrough.assign(
                        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
                    ) |
                    chat_answer_prompt
                    | chat
                    )

        if aux_context:
            return answer_chain.invoke({"aux_context": aux_context,
                                        "user_message": user_message})

        return answer_chain.invoke({"user_message": user_message})

    def rag_invoke(self, user_message: str,
                   system_message: str,
                   aux_context: str,
                   rag_context: str,
                   memory: Union[BaseChatMemory, Memory]):

        system_prompt = system_message
        print(f"User Message: {user_message} \nUser Context: {aux_context}")
        if aux_context:
            human_message_template = templates.human_message_template_rag_with_context
        else:
            human_message_template = templates.human_message_template_rag_without_context

        chat_answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=system_prompt
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
                    | self.chat_answer
                    )

        if aux_context:
            return answer_chain.invoke({"aux_context": aux_context,
                                        "user_message": user_message,
                                        "rag_context": rag_context})

        return answer_chain.invoke({"user_message": user_message,
                                    "rag_context": rag_context})

    def faq_invoke(self, user_message: str,
                         memory: Union[BaseChatMemory, Memory]):

        human_message_template = faq_query_template
        system_prompt = faq_system_message

        chat_answer_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=system_prompt
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
                | self.chat_answer
        )

        return answer_chain.invoke({"user_message": user_message})

    def get_search_query(self,
                         user_message: str,
                         memory: Union[BaseChatMemory, Memory]):

        human_message_template = rag_query_prompt

        chat_answer_prompt = ChatPromptTemplate.from_messages([
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
                | self.chat_answer
        )

        return answer_chain.invoke({"user_message": user_message})


class ConversationFlow:

    default_language_mapping = {
        'WCA': "EN",
        'WCM': "EN",
        'WCW': "EN",
        'WCI': "EN",
        'WCH': "EN",
        'WCHA': "CAR",
        'WCHC': "CAR",
        'WCMC': "ES",
        'WCB': "CH"
    }

    def __init__(self, bot: HRBot,
                 rag_sources_classifier: LLMClassifierAzure,
                 rag_retriever: IndexManager,
                 memory: Union[BaseChatMemory, Memory],
                 question_module: QuestionRecommender,
                 rag_category_mapping: dict[str, str] = None,
                 topic_to_rag_mapping: dict[str, str] = topic_to_rag_mapping,
                 topic_mapping: dict[str, str] = topic_mapping,
                 conversation_state: ConversationState = None,
                 language_classifier: LLMClassifierAzure = None,
                 translator: Translator = None,
                 rag_llm_query: bool = True,
                 wc_test: bool = False
                 ):
        """
        Conversation flow interface
        :param bot: LLM interface with invoke() and rag_invoke() methods
        :type bot: DiscoveryBot
        :param rag_sources_classifier: multilabel LLM classifier for static knowledge category recommendation
        :type rag_sources_classifier: LLMClassifierBedrock
        :param rag_retriever: RAG context manager
        :type rag_retriever: IndexManager
        :param rag_category_mapping: mapping between RAG data categories for classification and retriever
        :type rag_category_mapping: dict[str, str]
        :param memory: instance of langchain compatible memory
        :type memory: Union[BaseChatMemory, Memory]
        :param question_module: LLM module for clarification question recommendation
        :type question_module: QuestionRecommender
        :param conversation_state: session state handler instance
        :type conversation_state: ConversationState
        :param translator: translation module
        :type translator: Translator
        :param rag_llm_query: generate query for index search with LLM
        :type rag_llm_query: bool
        """
        self.bot = bot
        self.memory = memory

        self.rag_sources_classifier = rag_sources_classifier
        self.rag_retriever = rag_retriever
        self.rag_category_mapping = rag_category_mapping
        self.topic_to_rag_mapping = topic_to_rag_mapping
        self.topic_mapping = topic_mapping
        self.rag_llm_query = rag_llm_query

        self.language_classifier = language_classifier
        self.translator = translator
        self.language = None

        self.context_manager = ContextManager(test_mode=wc_test)
        self.classification = {}

        self.question_module = question_module

        if conversation_state is None:
            conversation_state = ConversationState('', '')
        self.conversation_state = conversation_state

    async def invoke(self, user_message: str, property_idx: str, user_id: str) -> str:
        """
        Make conversation step
        :param user_message: plain text message from user
        :type user_message: str
        :return: plain text message from AI assistant
        :rtype: str
        """

        print("=" * 50)
        print(f"Session state: USER: {user_id}, PROPERTY: {property_idx}")
        print(f"Memory state: {self.memory.load_memory_variables({})}")
        print("+" * 50)

        language = self.get_conversation_language(user_message)
        default_language = self.default_language_mapping.get(property_idx, 'EN')

        # check for FAQ
        faq_res = self.bot.faq_invoke(user_message, self.memory).content
        print("/?/" * 25)
        print(f"FAQ response: {faq_res}")
        print("/?/" * 25)
        if faq_res:
            if "NOT_A_FAQ" not in faq_res:
                print("FAQ detected")
                self.memory.save_context({"user": user_message}, {"assistant": faq_res})
                return faq_res

        # continue if clarification process is in progress
        if self.conversation_state.clarification_needed:
            clarification_res = self.clarify(user_message)
            if clarification_res is not None:
                clarification_res_lang = self.language_classifier.invoke(clarification_res)[0]
                if clarification_res_lang == language:
                    return clarification_res
                return self.translator(clarification_res, language)

        # get relevant RAG data sources
        topics = self.rag_sources_classifier.invoke_with_memory(user_message, self.memory)
        # Save classification results for debugging purposes
        self.classification['Topics'] = topics
        print(f"Topics: {topics}")
        topics_mapped = [self.topic_mapping.get(topic) for topic in topics]
        print(f"Topics mapped: {topics}")
        # get aux context
        aux_context = self.context_manager.get_context(user_id, topics_mapped)
        print(f'Auxiliary context: {aux_context}')

        rag_categories = [topic_to_rag_mapping.get(topic) for topic in topics_mapped]
        self.classification['RAG Categories'] = rag_categories
        print(f"RAG Categories: {topics}")
        print("+" * 50)
        # retrieve data from indexes
        if rag_categories and self.rag_llm_query:
            index_query = self.bot.get_search_query(user_message, self.memory).content
            print(f'Query for index search: /n {index_query}')

        else:
            index_query = user_message

        rag_context = await self.rag_retriever.retrieve(index_query,
                                                        rag_categories,
                                                        property_idx,
                                                        category_mapping=self.rag_category_mapping,
                                                        conversation_language=language,
                                                        property_language=default_language)

        self.conversation_state.rag_context = rag_context
        print(f"RAG context: {rag_context}")
        print("+" * 50)
        # dispatch logic
        print(">" * 50)
        clarification_res = self.clarify(user_message)
        # Whether the question is clarification    
        self.classification['Clarification Question'] = ['False' if (clarification_res is None) else 'True']
        if clarification_res is not None:
            print('Clarification needed')
            clarification_res_lang = self.language_classifier.invoke(clarification_res)[0]
            if clarification_res_lang == language:
                return clarification_res
            return self.translator(clarification_res, language)

        print('Clarification not needed')
        print("<" * 50)

        system_message = self.get_system_prompt()

        if rag_context:
            answer = self.bot.rag_invoke(user_message=user_message,
                                         system_message=system_message,
                                         aux_context=aux_context,
                                         rag_context=rag_context,
                                         memory=self.memory)
            assistant_message = answer.content
            self.memory.save_context({"user": user_message}, {"assistant": assistant_message})
            return assistant_message

        answer = self.bot.invoke(user_message=user_message,
                                 system_message=system_message,
                                 aux_context=aux_context,
                                 memory=self.memory)
        assistant_message = answer.content
        self.memory.save_context({"user": user_message}, {"assistant": assistant_message})
        return assistant_message

    def clarify(self, user_message: str) -> str | None:
        """
        Handle clarification logic based on conversation state and parameters
        :param user_message: plain text message from user
        :type user_message: str
        :return: clarification question or None
        :rtype: str | None
        """
        if self.conversation_state.clarification_counter == self.conversation_state.clarification_max_retries:
            return None
        aux_context, rag_context = self.conversation_state.get()
        flag, questions = self.question_module.invoke(user_message, aux_context, rag_context, memory=self.memory)
        if not flag or not questions:
            self.conversation_state.reset()
            return None

        assistant_message = questions[0]
        self.conversation_state.next()
        self.memory.save_context({"user": user_message}, {"assistant": assistant_message})
        return assistant_message

    def get_system_prompt(self) -> str:
        """
        Get system prompt based on conversation state and parameters
        :return: formatted system prompt
        :rtype: str
        """
        return templates.system_message_template

    def get_conversation_language(self, user_message: str) -> str:
        if self.language:
            return self.language
        language = self.language_classifier.invoke(user_message)[0]
        self.language = language
        print(f'Language set to {language}')
        return language

