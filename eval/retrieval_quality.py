import uuid
from app.session import SessionManager
from app.retrieval import retrieval_and_reranking
from app.ingestion import extract

manager = SessionManager()
filename = "d2l-en.pdf"
path = f"corpus/{filename}"
doc_bytes = open(path, "rb").read()
chunks, _, _ = extract(path)

session = manager.create_session(filename, doc_bytes, chunks)
query, top_chunks, _ = retrieval_and_reranking(session, "What's the difference between LSTM and GRU gating mechanisms?")
print(query)
print("--"*20)
print(top_chunks)
