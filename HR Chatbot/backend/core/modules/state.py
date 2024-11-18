class ConversationState:
    """
    State manager for a single conversation. Used to manage clarification questions loop
    and preserving context throughout clarification question loop
    """
    def __init__(self,
                 aux_context: str,
                 rag_context: str,
                 clarification_max_retries: int = 2):
        """
        :param aux_context: auxiliary context to be stored (initial value)
        :type aux_context: str
        :param rag_context: RAG context to stored (initial value)
        :type rag_context: str
        :param clarification_max_retries: maximal number of clarification questions in a row
        :type clarification_max_retries: int
        """
        self.aux_context: str = aux_context
        self.rag_context: str = rag_context
        self.clarification_needed: bool = False
        self.suggestive_question_needed: bool = False
        self.clarification_max_retries: int = clarification_max_retries
        self.clarification_counter: int = 1


    def reset(self) -> None:
        """
        Reset clarification loop counter
        :return: None
        :rtype: None
        """
        self.clarification_needed = False
        self.clarification_counter = 1

    def get(self) -> tuple[str, str]:
        """
        Get stored personal and RAG context (for clarification loop)
        :return: tuple of (personal context, RAG context)
        :rtype: tuple[str, str]
        """
        return self.aux_context, self.rag_context

    def next(self, clarification_needed: bool = True) -> None:
        """
        Make a step in clarification loop. Reset if needed
        :param clarification_needed: clarification needed at this step. False will reset the loop
        :type clarification_needed: bool
        :return: None
        :rtype: None
        """
        self.clarification_needed = clarification_needed
        if not clarification_needed:
            self.reset()
            return
        self.clarification_counter += 1
        if self.clarification_counter > self.clarification_max_retries:
            self.reset()
            return
