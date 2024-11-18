clarification_question_template = """
Your task now is to determine whether the question from the user is straightforward and clear, or it requires clarifications.

Here is a short list of each data source you already have access to:
<data sources>
- Company policies and procedures
- PTO (Paid Time Off) data and leave policies
- Company benefits
- Payroll data
- Property Scores data
- Onboarding and Hiring data
</data sources>

<<<aux_context_prompt>>>

<<<rag_prompt>>>

Check the following criteria when deciding whether clarification IS needed:
<example>
- user uses acronyms that may have multiple meanings (EXAMPLE: :"Tell me about MCWA")
- user question is not clear and may correspond to many unrelated topics  (EXAMPLE: "What are the policies?" )
- query contains so many typos that it's impossible to understand (EXAMPLE: "wgst are mu nenrfitz")
</examples>

Check the following criteria when deciding whether clarification IS NOT needed:
<example>
- user asks a general question that you already know the answer
- user asks a specific question related to their properties
- there is a mistake in wording, but the meaning is clear
- user asks a general question and the intention is clear (EXAMPLES: 
        > "Can you tell me about retirement plans?", 
        > "What benefits are available for me?", 
        > "Can you tell me about health benefits?")
- user intentions are clear based on recent messages
</examples>

<task>
Classify the following question and return the True if it requires clarification or False if not. 
If True, return top 2 clarification questions in a list that you think will help you to guide the user. 
The output should look like "True, [Question1, Question2]".
If False, return an empty list. The output should look like "False, []".
Do not include quotes around boolean value.
Do not use single quotes around the questions - always use double quotes.
Return the output in Python list. Do not return anything else.
</task>

<formatting>
Return only the Python list. Do not return anything else.
</formatting>

Process the following question:
{user_message}
"""

clarification_aux_context_prompt = """Also, here is some additional information that might be relevant to the question. 
If it is related to the question, use it to generate an answer:
<user data>
{aux_context}
</user data>"""

clarification_rag_prompt = """Also, here is some general knowledge about this question. 
This information is not mandatory to use but can bring additional insight into the context that the user has provided:
<general knowledge>
{rag_context}
</general knowledge>"""

clarification_sys_prompt = """You are "HR Bot", an HR counselor from WindCreek that will provide a guidance for company employees.
Keep the encouraging and polite tone and design the questions to keep user engaged in the conversation.
In case you're asking question because user query was to general - provide some suggestions on what user may explore.
"""