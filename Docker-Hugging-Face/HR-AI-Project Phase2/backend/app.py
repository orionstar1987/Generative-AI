import streamlit as st
from langchain_openai import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
import os
from core.conversation import HRBot, ConversationFlow

import yaml
from yaml.loader import SafeLoader

from core.modules.clarification import QuestionRecommender
from core.modules.classifier import LLMClassifierAzure
from core.modules.retriever import IndexManager
from core.modules.state import ConversationState
from core.templates import classification as classification_templates
from core.templates.clarification import clarification_question_template, clarification_aux_context_prompt, \
    clarification_rag_prompt, clarification_sys_prompt
from core.loaders.config import local_index_config
from core.modules.memory import MemoryWithSummary

# Load the icon image for the Streamlit page.
# Set Streamlit page configuration
st.set_page_config(page_title='HR Assistant', layout='wide')

AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')

AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')

# Env to run application
local = True
authentication_status = True
# Check if the user is authenticated
if authentication_status:
    # Initiate variables
    if 'selected_user' not in st.session_state or 'user_id' not in st.session_state:
        st.session_state['selected_user'] = 'John Doe'
        st.session_state['user_id'] = '1234'
        st.session_state['property'] = 'USA'

    if 'memory' not in st.session_state:
        st.session_state.memory = []

    if "history" not in st.session_state:
        st.session_state.history = []

    if "debug_information" not in st.session_state:
        st.session_state['debug_information'] = False

    # Function to initiate and run a conversation
    def get_conversation_chain():

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

        embedding_model = AzureOpenAIEmbeddings(model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
                                                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                                                openai_api_key=AZURE_OPENAI_API_KEY)

        st.session_state.memory = MemoryWithSummary(size=3, llm=chat_llm)

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



        rag_retriever = IndexManager(embedding_model, local_index_config)
        print('Building vector store')
        rag_retriever.load_or_build()

        print("Initializing conversation flow")
        conversation_chain = ConversationFlow(bot,
                                            rag_sources_classifier=topic_classifier,
                                            rag_retriever=rag_retriever,
                                            question_module=question_module,
                                            memory=st.session_state.memory)

        # LLM classification results for debugging purposes
        st.session_state.classification = conversation_chain.classification

        return conversation_chain

    # Start defining the sidebar content
    with st.sidebar:

        # Welcome message for the authenticated user
        # st.markdown(f'Welcome, **{st.session_state["name"]}**')
        # Logout button for the authenticated user
        # authenticator.logout('Logout', 'main')

        # Clear history by pressing a button
        clear_history = st.button("Clear Chat History")
        if clear_history:
            st.session_state.history = []
            st.session_state.memory.clear()
            st.session_state.conv.conversation_state = ConversationState('', '')

        # Tabs as dropdowns
        tab = st.selectbox("Tab:",
                            ['Chat', 'Auxiliary Information'],
                            index=0)

        debug_information = st.checkbox("Show debug information", value=False)

        # Separator line
        st.markdown("---")

        # Select user for simulation in app
        selected_user = st.selectbox("Select user for simulation:",
                                    ['John Doe'])

        # if user is changed 
        if selected_user != st.session_state['selected_user']:
            st.session_state['selected_user'] = 'John Doe'
            st.session_state['user_id'] = '1234'
            st.session_state['property'] = 'USA'
            
            st.session_state.history = []
            st.session_state.memory.clear()
            
            st.session_state.conv = get_conversation_chain()

        if debug_information != st.session_state['debug_information']:

            st.session_state['debug_information'] = debug_information
    
    # Format LLM classification results as a part of response
    def format_print_categories(category_dict) -> str:

        keys = list(category_dict.keys())
        values = list(category_dict.values())
    
        init_string = "\n---\n**DEBUG.\nClassification Outputs:**\n"
        for i, key in enumerate(keys):
            line_i = "***" + key + "***: " + ", ".join(values[i])
            init_string += f"{i+1}. {line_i}\n"

        return init_string

    if tab == "Chat":
        st.title("Chat with HR Assistant")

        if 'conv' not in st.session_state:
            st.session_state.conv = get_conversation_chain()
        
        # Combine conversation history
        for i, message in enumerate(st.session_state.history):
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["user"])
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["assistant"])

        user_question = st.chat_input("How can I help you?", key="user_question_input")

        if user_question:
            response = st.session_state.conv.invoke(user_question)
            if st.session_state['debug_information']:
                st.session_state.history +=[{"user": user_question, "assistant": response + " \n\n\n " + format_print_categories(st.session_state.classification)}]
            else:
                st.session_state.history +=[{"user": user_question, "assistant": response}]
            st.rerun()
