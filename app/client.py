import os
from dotenv import load_dotenv
load_dotenv()
from ollama import chat
from groq import Groq
ENV = os.getenv("ENV")

if ENV == "production":
    inference_client = Groq(api_key=os.environ.get("GROQ_INFERENCE_KEY"))

def llm(user_prompt: str, system_prompt: str = None) -> str:

    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": user_prompt})

    if ENV == "local":
        response = chat(
            "llama3.2:3b",
            messages=messages
        )
        return response["message"]["content"]

    elif ENV == "production":
        response = inference_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
