translation_prompt = f"""
TASK: Your task is to translate given message to <<<language>>> 
<task>
Do the following steps:
      1. correct spelling and grammatical mistakes of the text: ```<<<text>>>```.
      2. detect the language of the corrected text.
      3. translate the corrected text to <<<language>>>. 
         Do not interpret or change the text. The result should be a direct translation of the text.
</task>
<example> 
EXAMPLE: input: ```Das ist ein Hund```; ```Deutsch```; ```child``` 
      1. Das ist ein Hund 
      2. Deutsch
      3. This is a dog
</example>
<output>
OUTPUT: Output only the translated message (result of step 3)
</output>
""".strip()

translation_system_prompt = """You are a translator gpt responsible for accurate translations of user queries, 
documents and AI assistant responses.""".strip()
