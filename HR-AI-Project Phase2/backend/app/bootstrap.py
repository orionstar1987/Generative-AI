from azure.core.credentials import AzureKeyCredential
from langchain_openai import AzureChatOpenAI
import os
from core.conversation import HRBot, ConversationFlow

from core.modules.clarification import QuestionRecommender
from core.modules.classifier import LLMClassifierAzure
from core.modules.utils import Translator
from core.modules.retriever import IndexManager
from core.templates import classification as classification_templates
from core.templates.clarification import clarification_question_template, clarification_aux_context_prompt, \
    clarification_rag_prompt, clarification_sys_prompt
from core.modules.memory import MemoryWithSummary

# Function to initiate and run a conversation
def get_conversation_chain() -> ConversationFlow:

    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = "2024-02-01"

    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

    AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
    AZURE_AI_SEARCH_KEY = os.getenv("AZURE_AI_SEARCH_KEY")

    TEST_MODE = os.getenv("WC_TEST") == "True"

    chat_llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_key=AZURE_OPENAI_API_KEY,
        temperature=0.1
    )
    answer_llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        openai_api_key=AZURE_OPENAI_API_KEY,
        temperature=0.0
    )

    memory = MemoryWithSummary(size=3, llm=chat_llm)

    bot = HRBot(chat_standalone=chat_llm,
                chat_answer=answer_llm)

    topic_classifier = LLMClassifierAzure(answer_llm,
                                          classification_templates.rag_classification_template,
                                          categories=classification_templates.rag_categories)

    question_module = QuestionRecommender(llm=chat_llm,
                                          template=clarification_question_template,
                                          rag_prompt=clarification_rag_prompt,
                                          user_context_prompt=clarification_aux_context_prompt,
                                          system_prompt=clarification_sys_prompt)

    search_credential = AzureKeyCredential(AZURE_AI_SEARCH_KEY)
    search_endpoint = AZURE_AI_SEARCH_ENDPOINT

    translator = Translator(answer_llm)

    print('Configuring vector store')
    rag_retriever = IndexManager(search_endpoint, search_credential, translator)

    language_classifier = LLMClassifierAzure(answer_llm,
                                             classification_templates.language_classification_prompt,
                                             categories=classification_templates.languages)

    print("Initializing conversation flow")
    conversation_chain = ConversationFlow(bot,
                                          rag_sources_classifier=topic_classifier,
                                          rag_retriever=rag_retriever,
                                          question_module=question_module,
                                          memory=memory,
                                          language_classifier=language_classifier,
                                          translator=translator,
                                          wc_test=TEST_MODE
                                          )

    return conversation_chain


class FlowManager:
    def __init__(self):
        self.flows = dict()

    def get(self, user_id: str | int, session_id: str | int) -> ConversationFlow:
        flow_obj = self.flows.get(user_id)
        if not flow_obj:
            flow = get_conversation_chain()
            self.flows[user_id] = {'session_id': session_id, 'flow': flow}
            return flow

        if flow_obj.get('session_id') != session_id:
            flow = get_conversation_chain()
            self.flows[user_id] = {'session_id': session_id, 'flow': flow}
            return flow

        return flow_obj.get('flow')
