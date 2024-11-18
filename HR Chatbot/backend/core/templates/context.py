rag_query_prompt = """
Below is a history of the conversation so far, 
and a new question asked by the user that needs to be answered by searching in a corporate HR document knowledge base.

Generate a search query based on the conversation and the new message from the user.

Conversation history:
{history}

Message from the user: 
{user_message}

Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
Do no include any search operators like "site:" in the search query terms.
Do not include any text inside [] or <<>> in the search query terms.
Do not include any special characters like '+'.
If you cannot generate a search query, return the latest user message.
If user message is very short, but he expects lot of different information - try to expand the query to search for
 as much relevant documents as possible.
""".strip()