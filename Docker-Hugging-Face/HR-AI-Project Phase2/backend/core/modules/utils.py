from core.modules.base import Module
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from core.templates.translation import translation_prompt, translation_system_prompt

class Translator(Module):

    lang_code_to_name = {
        "EN": "English",
        "ES": "Spanish",
        "CH": "Chinese",
        "NL": "Dutch",
        "CAR": "Papiamento"
    }

    def __init__(self,
                 llm: AzureChatOpenAI,
                 template: str = translation_prompt,
                 sys_message: str = translation_system_prompt):

        super().__init__()
        self.llm = llm
        self.template = template
        self.sys_message = sys_message

    def invoke(self, text: str, target_language: str):
        prompt = self.template.replace('<<<text>>>', text) \
                                     .replace('<<<language>>>', target_language)

        messages = [
            SystemMessage(content=self.sys_message),
            HumanMessage(content=prompt)
        ]

        chat_prompt = ChatPromptTemplate.from_messages(messages)

        response = self.llm(
            chat_prompt.format_prompt().to_messages()
        )

        translation = response.content.strip()
        return translation

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)
