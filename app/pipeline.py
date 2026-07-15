from .ingestion import extract
from .session import SessionManager, ChatTurn
from .retrieval import retrieval_and_reranking
from .context import generate_context
from .client import generate
import time

manager = SessionManager()

def pipeline(file_path: str, query: str):
    t = time.perf_counter()

    chunks, _, _ = extract(file_path)
    print(f"Time to extract {file_path}: {time.perf_counter() - t:.4f}s")
    t = time.perf_counter()

    file_bytes = open(file_path, "rb").read()
    print(f"Time to convert file into bytes: {time.perf_counter() - t:.4f}s")
    t = time.perf_counter()

    session = manager.create_session(file_path, file_bytes, chunks)
    print(f"Time to create session: {time.perf_counter() - t:.4f}s")
    t = time.perf_counter()

    top_k_chunks, _ = retrieval_and_reranking(session, query)
    print(f"Time to retrieve relevant chunks: {time.perf_counter() - t:.4f}s")
    t = time.perf_counter()

    context, _ = generate_context(top_k_chunks)
    print(f"Time to generate context: {time.perf_counter() - t:.4f}s")
    t = time.perf_counter()

    response = generate("", context, query)
    print(f"Time to generate response: {time.perf_counter() - t:.4f}s")

    print(response)
    content = f"""
    query: {query}\n
    response: {response}
    """
    exchange = ChatTurn("user", content)

    return response

pipeline("corpus/d2l-en.pdf", "What embedding dimension and number of attention heads does the base BERT model use?")
