from .client import llm
import json

def parse_suggestions(response: str) -> list[str]:
    try:
        parsed = json.loads(response.strip())

        if not isinstance(parsed, list):
            return []

        if not all(isinstance(item, str) for item in parsed):
            return []

        return parsed

    except json.JSONDecodeError:
        return []

def follow_up(query: str, response:str) -> list[str]:
    PROMPT = f"""
    You are a helpful assistant. Based on the conversation below,
    suggest three follow up questions the user might want to ask
    about the document they are reading.

    The questions should:
    - Be specific and answerable from the same document
    - Build naturally on what was just discussed
    - Cover different angles or dig deeper into the topic

    Return exactly three questions as a JSON array of strings.
    No preamble, no explanation, just the array.

    Example output format:
    ["Question one?", "Question two?", "Question three?"]

    USER QUESTION:
    {query}

    ASSISTANT ANSWER:
    {response}
    """
    response = llm(user_prompt=PROMPT)
    return parse_suggestions(response)
