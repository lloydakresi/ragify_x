# RAGify

A generalized document chat system. Upload any PDF and have a grounded conversation with it. Every answer is cited back to the exact page it came from. If the answer is not in the document the system says so rather than making things up.

Built as Project 3 of 4 in a production ML portfolio. v2 adds multimodal support for documents with images and diagrams. v3 adds knowledge graph retrieval for hierarchical document corpora.

**Live demo:** [lakresi-ragify.hf.space](https://huggingface.co/spaces/lakresi/ragify)

**GitHub:** [github.com/lloydakresi/ragify_x](https://github.com/lloydakresi/ragify_x)

---

## What It Does

Standard document search is keyword based. If you do not use the exact right words you miss relevant content. RAGify uses semantic search to find content by meaning, not by word match. The answers are grounded strictly in the uploaded document; the model cannot draw on outside knowledge, which means citations are always traceable and hallucinations are structurally prevented rather than just prompted away.

---

## The Pipeline

Six stages run on every query:

```
1. Ingestion        PDF text extraction and cleaning via pdfplumber
2. Chunking         Sentence aware splitting with 75 token overlap
                    to preserve context at chunk boundaries
3. Embedding        Chunks embedded with all-MiniLM-L6-v2 and
                    stored in an in-memory ChromaDB collection
4. Retrieval        Top 75 candidate chunks retrieved by cosine
                    similarity against the embedded query
5. Reranking        Cross-encoder reranks candidates to top 5
                    using joint query-chunk scoring
6. Generation       Llama 3 8B via Groq generates a grounded
                    answer with page citations from the top 5 chunks
```

Each session gets its own isolated in-memory ChromaDB collection that is discarded when the session ends. No user data persists between sessions.

---

## Corpus Statistics (D2L, used as test corpus)

| Metric | Value |
|---|---|
| Pages processed | 1,151 |
| Chunks produced | 5,908 |
| Average chunk length | 399 tokens |

---

## Evaluation (RAGAS on D2L chapters 11 to 16)

| Metric | Score | What it measures |
|---|---|---|
| Faithfulness | 0.8977 | Are answers supported by retrieved context |
| Context precision | 0.9411 | Are retrieved chunks actually relevant to the query |
| Context recall | 0.7417 | Does retrieval find all relevant content in the document |
| Answer relevancy | NaN | Skipped — requires an embedding model incompatible with current setup |

Faithfulness of 0.897 means the model stays grounded in the retrieved context for nearly 90% of claims. Context precision of 0.941 means the retrieve and rerank pipeline is returning highly relevant chunks. Context recall of 0.742 indicates some relevant content is occasionally missed, which is expected for a document as dense as D2L where the same concept appears across many sections.

---

## Known Limitations

Scanned PDFs and image heavy documents extract poorly. Text extraction works best on fully digital PDFs with clean text layers. This is addressed in v2 with multimodal document support.

Context recall is bounded by chunk size and retrieval candidate count. For very long answers that draw on multiple sections of a document the pipeline may miss some relevant chunks. Increasing the candidate set from 75 to 150 would improve recall at the cost of reranking latency.

Answer relevancy could not be computed with the current evaluation setup due to an embedding model compatibility issue with the RAGAS version used. This will be measured in a follow up evaluation run.

The system is optimized for factual question answering over technical documents. Open ended creative or analytical questions that require synthesis across the full document will perform worse than targeted factual queries.

---

## Running Locally

Prerequisites: Python 3.10+, Ollama

```bash
git clone https://github.com/lloydakresi/ragify_x
cd ragify_x
pip install -r requirements.txt
```

Pull the local model via Ollama:

```bash
ollama pull llama3.1:8b
```

Set your environment:

```bash
cp .env.example .env
# set ENV=local in .env
```

Run:

```bash
python app.py
```

The app runs on http://localhost:7860. Upload any PDF and start asking questions.

---

## Project Structure

```
ragify_x/
├── app.py                  Gradio interface and session routing
├── app/
│   ├── ingestion.py        PDF extraction and chunking
│   ├── session.py          Session manager and ChromaDB lifecycle
│   ├── retrieval.py        Bi-encoder retrieval and cross-encoder reranking
│   ├── context.py          Context string construction
│   ├── generate.py         LLM call via Groq or Ollama
│   ├── history.py          Conversation history management
│   ├── follow_up.py        Follow up question generation
│   └── pipeline.py         End to end query pipeline
├── requirements.txt
└── README.md
```

---

## Roadmap

v2 — Multimodal support. Handle documents with images, charts, and diagrams by captioning visual content and making it retrievable alongside text.

v3 — Knowledge graph retrieval. Build a graph over hierarchical document corpora where queries extract and prune a relevant subgraph rather than flat chunks. Designed for technical manuals, legal documents, and any corpus with rich cross-document relationships.

---

## Related

[Project 1 — ArXiv Semantic Search](https://github.com/lloydakresi/arxiv_semantic_search)

[Project 2 — Toxic Comment Moderator](https://github.com/lloydakresi/toxic_comment_moderator_api)
