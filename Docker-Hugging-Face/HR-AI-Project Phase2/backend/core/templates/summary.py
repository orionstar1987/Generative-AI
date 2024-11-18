mem_summary_template = """You will be presented with the history of a conversation between human user and AI assistant.
History consists of two parts: last messages and summary of earlier messages:
<summary>
<<<summary>>>
</summary>
<messages>
<<<message>>>
</messages>
<task>
Your task is to summarise the texts provided in maximum <<<n_words>>> words.
Keep any keywords or names that user used in the summary. 
Make sure not to loose any personal details of the user if provided.
Focus on information describing overall user profile. 
DO NOT include anything except the summary.
DO NOT include description of your task.
Keep you summary as concise as possible.
</task>
"""