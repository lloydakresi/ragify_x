from .ingestion import extract
from .session import SessionManager, Session
from .retrieval import retrieval_and_reranking
from .context import generate_context
from .generate import generate
from .history import history_management, build_history_string
from .follow_up import follow_up
import time

manager = SessionManager()

def ingest(file_path:str):
    t = time.perf_counter()
    chunks, _, _ = extract(file_path)
    print(f"Time to extract {file_path}: {time.perf_counter() - t:.4f}s")
    t = time.perf_counter()

    file_bytes = open(file_path, "rb").read()
    print(f"Time to convert file into bytes: {time.perf_counter() - t:.4f}s")
    t = time.perf_counter()

    session = manager.create_session(file_path, file_bytes, chunks)
    print(f"Time to create session: {time.perf_counter() - t:.4f}s")
    return session


def pipeline(session: Session, query: str) -> tuple[str, list[str]]:
    try:
        t = time.perf_counter()
        top_k_chunks, _ = retrieval_and_reranking(session, query)
        print(f"Time to retrieve relevant chunks: {time.perf_counter() - t:.4f}s")

        t = time.perf_counter()
        context, _ = generate_context(top_k_chunks)
        print(f"Time to generate context: {time.perf_counter() - t:.4f}s")

        t = time.perf_counter()
        history = build_history_string(session)
        print(f"Time to generate history: {time.perf_counter() - t:.4f}s")

        t = time.perf_counter()
        response = generate(history, context, query)
        print(f"Time to generate response: {time.perf_counter() - t:.4f}s")

        print(response)
        t = time.perf_counter()
        follow_up_questions = follow_up(query, response)
        print(follow_up_questions)
        print(f"Time to generate follow-up questions: {time.perf_counter() - t:.4f}s")


        if len(session.chat_history) + 2 >= session.chat_history.maxlen:
            t = time.perf_counter()
            history_management(session)
            print(f"Time to generate summary: {time.perf_counter() - t:.4f}s")

        session.add_turn("user", query)
        session.add_turn("assistant", response)

        return response, follow_up_questions
    except Exception as e:
        print(f"Pipeline failed:{e}")
        return "Something went wrong processing your question. Please try again.", []
