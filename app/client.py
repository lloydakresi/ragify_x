import os
from dotenv import load_dotenv
load_dotenv()
from ollama import chat
from groq import Groq
ENV = os.getenv("ENV")

inference_client = Groq(api_key=os.environ.get("GROQ_INFERENCE_KEY"))

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
    {history}

    RETRIEVED DOCUMENT SECTIONS:
    {context}

    USER QUESTION:
    {query}

    Provide a clear, direct answer followed by your citations."""

    if ENV == "local":
        response = chat("llama3.2:3b",
                        messages=[{"role":"system", "content":SYSTEM_PROMPT},
                        {"role":"user", "content":USER_PROMPT},
                        ])
        return response.message.content
    elif ENV == "production":
        response = inference_client.chat.completions.create(
            messages=[{"role":"system", "content":SYSTEM_PROMPT},
                        {"role":"user", "content":USER_PROMPT},
                        ],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
