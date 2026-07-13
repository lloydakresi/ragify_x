import torch
from sentence_transformers import CrossEncoder
from session import Session

_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", activation_fn=torch.nn.Sigmoid())
def retrieval_and_reranking(session:Session, query:str, n:int=5):
    collection = session.collection
    result = collection.query(
        query_texts = [query],
        n_results = 50,
        include = ["documents"]
    )
    docs = result["documents"][0]
    scores = _model.rank(query, docs)
    top_k_idxs = [score["corpus_id"] for score in scores][:n]
    top_k_ids = []
    for score in top_k_idxs:
        top_k_ids.append(result["ids"][0][score])
    top_k_papers = collection.get(ids=top_k_ids)
    return top_k_papers, n
