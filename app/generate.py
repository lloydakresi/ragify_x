from .client import llm
SYSTEM_PROMPT = """
You are a document assistant. The user has uploaded a document
and wants to have a conversation about its contents.

Answer the user's question using the retrieved document sections
AND the conversation history provided below. If the user refers
to a previous answer or asks for elaboration, use the conversation
history to understand what they are referring to, then answer
from the document sections.

For every factual claim cite the source using [Page X].

If the answer cannot be found in the document sections or
conversation history, say exactly: "I could not find the answer
to that question in the uploaded document." Do NOT guess or infer.
"""

def generate(history, context, query):
    USER_PROMPT=f"""CONVERSATION HISTORY:
    {history}\n

    RETRIEVED DOCUMENT SECTIONS:
    {context}\n

    USER QUESTION:
    {query}

    Provide a clear, direct answer followed by your citations."""
    response = llm(system_prompt=SYSTEM_PROMPT, user_prompt=USER_PROMPT)
    return response
