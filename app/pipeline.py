from .ingestion import extract
from .session import SessionManager
from .retrieval import retrieval_and_reranking
from .context import generate_context
from .client import generate

manager = SessionManager()

def pipeline(file_path:str, query:str):
    chunks, _, _ = extract(file_path)
    file_bytes = open(file_path, "rb").read()
    session = manager.create_session(file_path, file_bytes, chunks)
    top_k_chunks, _ = retrieval_and_reranking(session, query)
    context, _ = generate_context(top_k_chunks)
    response = generate("", context, query)
    print(response)
    return response

pipeline("corpus/d2l-en.pdf", "How does the model know what to pay attention to?")
