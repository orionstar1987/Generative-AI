user_message_template = """
Here is the conversation history:
{history}

Use the history only as additional context if Query contains ambiguous terms.
Classify the following Query:
{query}
"""

rag_classification_template = f"""
You are a robust and well-trained intent classifier designed to identify which data sources to use for accurate 
RAG (Retrieval-Augmented Generation) retrieval.

There are three available data sources with the following descriptions:
<data sources>
<<<categories>>>
</data sources>

<task>
Your task is to analyze the provided user Query and return a list of data sources, that can provide value with contextual search.
- It's a multilabel classification task: Query can be classified with multiple classes or NONE classes.
- If NONE of the data sources are relevant, return an empty list: []
- Do not assign classes if only general terms are in the Query that don't provide enough context for accurate classification.
- Take message history into account, but classify only the current Query. Use the history only as additional context.
- If language of the Query is not English - translate the message into English before performing classification

<formatting>
Return only the Python list. Do not return anything else.
</formatting>
"""

rag_categories = {'Policies and Procedures': """use this class if the user Query contains:
  - Questions about company guidelines 
  - Queries about company regulations 
  - Example questions include:
  > What is my employee ID?  
  > How do I report my supervisor/manager? 
  > How do I apply for Helping Hearts and Hands?""",
                  'Leave Questions': """use this class if the user Query contains:
  - Queries about paid time off (PTO)
  - Questions about company leave policies
  - Example questions include: 
  > Can I cash in my PTO? 
  > Can I give my PTO to another team member that is sick? 
  > When can I start seeing my PTO and take it? 
  """,
                  'Benefits': """use this class if the user Query contains:
  - Clearly mention about employee benefits
  - Questions about insurance
  - Examples of potential user questions include: 
  > What benefits do I have?  
  > How long after I quit will I have insurance? 
  > What is my emergency room deductible? 
  > When can I sign up for benefits?  
  > How do I contact my 401K?""",

                  'BSwift': """use this class if the user Query contains:
  - Inquiries to enroll in benefit program
  - Inquiries to resign from a benefit program
  - Questions about personal details of a benefit program (e.g. current balance in a saving plan)
  - Inuiries to change terms of a benefit program 
""",

                  'Onboarding and Hiring': """use this class only for Queries about new hires and employee processes """,
'Payroll': """use this class if the user Query is related to wages, deductions, and payroll. Example questions include:
  - How do I access my W2? 
  - Questions about insurance
  - What days do I receive shift premium? 
  - How do I print my check stub? 
  - How do I change my direct deposit? 
  - Who do I talk to when my bonus is not right? 
  - What is the company code on Greenshades? """,

'Property Scores': """use this class if the user Query requires information on scores for specific properties""",

'Other': """use this class when other categories can't be matched. 
Every topic that might be related to company policies, expectations from employees, company values, company specific terms etc. 
should fall to this category if not covered elsewhere. 
No category should be assigned only when you're sure that the query is not related to company policies and processes"""
                  }


language_classification_prompt = """
You are a robust and well-trained language recognition system. 
Your task is to detect in what language the message is written.

There are five available languages:
<languages>
<<<categories>>>
</languages>

<task>
Your task is to analyze the provided user Query and return a one-element list of region code corresponding to detected language.
- It's a single label classification task: Query can be classified with single class or NONE.
- If NONE of the languages can be matched, return a list with code OTHER: ['OTHER']

<formatting>
Return only the Python list. Do not return anything else.
</formatting>

Classify the following Query:
"""

languages = {"EN": "English",
            "ES": "Spanish",
            "CH": "Mandarin or other dialect of modern Chinese",
            "NL": "Dutch",
            "CAR": "Papiamento"}
