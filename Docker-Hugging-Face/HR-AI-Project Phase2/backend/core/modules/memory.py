from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from .base import Memory
import queue
from typing import Dict, Any
from core.templates.summary import mem_summary_template
import json


class QueueMemory(Memory):
    """Simple fixed size queue memory (FIFO)"""
    def __init__(self, size: int,
                 ai_role: str = 'Assistant',
                 human_role: str = 'User',
                 return_messages: bool = True):
        """
        :param size: memory buffer size
        :type size: int
        :param ai_role: AI role name in this conversation
        :type ai_role: str
        :param human_role: User role name in this conversation
        :type human_role: str
        :param return_messages: return messages as langchain BaseMessage instead of plain strings
        :type return_messages: bool
        """
        super().__init__(size, ai_role, human_role, return_messages=return_messages)
        self.window = queue.Queue(maxsize=self.size)

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        input = inputs.pop(self.human_role)
        input_kwargs = inputs

        output = outputs.pop(self.ai_role)
        output_kwargs = outputs

        payload = {self.human_role: input,
                   self.ai_role: output,
        }

        if input_kwargs:
            payload.update({f'{self.human_role}_kwargs': input_kwargs})

        if output_kwargs:
            payload.update({f'{self.ai_role}_kwargs': output_kwargs})
        if not self.window.full():
            self.window.put(payload)
            return
        self.window.get()
        self.window.put(payload)

    def clear(self):
        self.window = queue.Queue(maxsize=self.size)

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        messages = []
        for msg in list(self.window.queue):
            if self.return_messages:
                messages.extend(self._msg_to_msg(msg))
                continue
            messages.append(self._msg_to_str(msg))

        if inputs:
            print(inputs)
            if self.return_messages and inputs.get(self.human_role):
                messages.append(HumanMessage(content=inputs.get(self.human_role)))
            elif inputs.get(self.human_role):
                messages.append(f"{self.human_role}: {inputs.get(self.human_role)}")

        return {'history': messages}


class MemoryWithSummary(Memory):
    """FIFO memory with fixed size queue and summary for messages outside window"""
    def __init__(self,
                 size: int,
                 llm: AzureChatOpenAI,
                 return_messages: bool = True,
                 summary_max_len: int = 500,
                 ai_role: str = 'assistant',
                 human_role: str = 'user',
                 **kwargs
                 ):
        """

        :param size: FIFO memory buffer size
        :type size: int
        :param llm: langchain AzureChatOpenAI client
        :type llm: langchain_openai.AzureChatOpenAI
        :param return_messages: return messages as langchain BaseMessage instead of plain strings
        :type return_messages: bool
        :param summary_max_len: maximum lenght of summary part (in tokens)
        :type summary_max_len: int
        :param ai_role: AI role name in this conversation
        :type ai_role: str
        :param human_role: User role name in this conversation
        :type human_role: str
        """
        super().__init__(size, ai_role, human_role, return_messages=return_messages)
        self.window = queue.Queue(maxsize=self.size)
        self.summary = ""
        self.summary_max_len = summary_max_len
        self.llm = llm
        self.model_kwargs = kwargs

    def clear(self):
        self.window = queue.Queue(maxsize=self.size)
        self.summary = ""

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        input = inputs.pop(self.human_role)
        input_kwargs = inputs

        output = outputs.pop(self.ai_role)
        output_kwargs = outputs

        payload = {self.human_role: input,
                   self.ai_role: output,
        }

        if input_kwargs:
            payload.update({f'{self.human_role}_kwargs': input_kwargs})

        if output_kwargs:
            payload.update({f'{self.ai_role}_kwargs': output_kwargs})
        if not self.window.full():
            self.window.put(payload)
            return

        oldest = self.window.get()
        self.window.put(payload)
        self._extend_summary(oldest)

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        messages = []
        if self.summary:
            if self.return_messages:
                prompt = HumanMessage(content='Provide a summary of earlier conversation')
                summary = AIMessage(content=self.summary)
                messages.extend([prompt, summary])
            else:
                summary = f"Summary of earlier messages: {self.summary}"
                messages.append(summary)

        for msg in list(self.window.queue):
            if self.return_messages:
                messages.extend(self._msg_to_msg(msg))
                continue
            messages.append(self._msg_to_str(msg))

        if inputs:
            print(inputs)
            if self.return_messages and inputs.get(self.human_role):
                messages.append(HumanMessage(content=inputs.get(self.human_role)))
            elif inputs.get(self.human_role):
                messages.append(f"{self.human_role}: {inputs.get(self.human_role)}")

        return {'history': messages}


    def _extend_summary(self, oldest: Dict[str, Any]) -> None:

        prompt = mem_summary_template.replace('<<<n_words>>>', str(self.summary_max_len)) \
                                     .replace('<<<summary>>>', self.summary) \
                                     .replace('<<<message>>>', self._msg_to_str(oldest))

        messages = [
            HumanMessage(content=prompt)
        ]

        chat_prompt = ChatPromptTemplate.from_messages(messages)

        response = self.llm(
            chat_prompt.format_prompt().to_messages(),
            **self.model_kwargs
        )

        self.summary = response.content.strip()
        return


