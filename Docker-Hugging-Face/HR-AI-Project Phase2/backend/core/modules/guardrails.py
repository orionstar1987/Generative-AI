from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter
from .base import Module, Memory


class GuardrailAgent(Module):
    def __init__(self, chat: BaseChatModel, prompt: str):
        super().__init__()

        self.chat = chat
        self.prompt = prompt

    def invoke(self, user_message: str,
               system_message: str,
               aux_context: str,
               rag_context: str,
               memory: Memory,
               ai_message: str):

        system_prompt = system_message
        print(f"User Message: {user_message} \nUser Context: {aux_context}")

        human_message_template = self.prompt

        if not aux_context:
            human_message_template = human_message_template.replace('{aux_context}', '')

        if not rag_context:
            human_message_template = human_message_template.replace('{rag_context}', '')

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
                | self.chat
        )

        if aux_context and rag_context:
            return answer_chain.invoke({"aux_context": aux_context,
                                        "user_message": user_message,
                                        "rag_context": rag_context})
        elif rag_context:
            return answer_chain.invoke({"user_message": user_message,
                                    "rag_context": rag_context})

        elif aux_context:
            return answer_chain.invoke({"aux_context": aux_context,
                                        "user_message": user_message})

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

