import chromadb
from ingestion import extract
def embeddings(file_path):
    client = chromadb.Client()
    v_db = client.get_or_create_collection(name="emb_db")
    chunks, _, _ = extract(file_path)
    v_db.add(
        ids = chunks["ids"],
        documents=chunks["text"],
        metadatas=chunks["metadata"]
    )
    return v_db
