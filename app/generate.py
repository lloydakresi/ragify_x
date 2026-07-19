from .client import llm
SYSTEM_PROMPT = f"""
You are a document assistant. The user has uploaded a document
and wants to have a conversation about its contents.

Answer the user's question using ONLY the content from the
retrieved document sections provided below. Do not use any
knowledge from outside these sections.

For every factual claim in your answer cite the source using
this exact format: [Page X]. If information comes from multiple
pages cite each one.

If the answer to the question cannot be found in the provided
sections, say exactly this: "I could not find the answer to
that question in the uploaded document." Do NOT guess or infer.
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
