import time
import uuid
import hashlib
from dataclasses import dataclass, field
from typing import Optional
import chromadb
from chromadb.utils import embedding_functions

@dataclass
class ChatTurn:
    role: str          # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class Session:
    session_id: str
    filename: str
    doc_hash: str
    collection: chromadb.Collection
    chat_history: list[ChatTurn] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)

    def touch(self):
        self.last_accessed = time.time()

    def add_turn(self, role: str, content: str):
        self.chat_history.append(ChatTurn(role, content))
        self.touch()


class SessionManager:
    def __init__(self, max_sessions: int = 10, ttl_seconds: int = 3600):
        self.client = chromadb.EphemeralClient()  # in-memory
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.sessions: dict[str, Session] = {}
        self.max_sessions = max_sessions
        self.ttl_seconds = ttl_seconds

    def _hash_file(self, file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()[:16]

    def create_session(self, filename: str, file_bytes: bytes, chunks: dict[str, list]) -> Session:
        self._evict_if_needed()

        doc_hash = self._hash_file(file_bytes)
        # reuse an existing session if the same doc is already loaded
        for s in self.sessions.values():
            if s.doc_hash == doc_hash:
                s.touch()
                return s

        session_id = str(uuid.uuid4())
        collection = self.client.create_collection(
            name=f"doc_{session_id}",
            embedding_function=self.embed_fn,
        )
        collection.add(
            documents=chunks["text"],
            ids=[f"{session_id}_{i}" for i in range(len(chunks))],
            metadatas=chunks["metadata"]
        )

        session = Session(
            session_id=session_id,
            filename=filename,
            doc_hash=doc_hash,
            collection=collection,
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self.sessions.get(session_id)
        if session:
            session.touch()
        return session

    def close_session(self, session_id: str):
        session = self.sessions.pop(session_id, None)
        if session:
            self.client.delete_collection(session.collection.name)

    def _evict_if_needed(self):
        now = time.time()
        # TTL eviction first
        expired = [sid for sid, s in self.sessions.items()
                   if now - s.last_accessed > self.ttl_seconds]
        for sid in expired:
            self.close_session(sid)

        # LRU eviction if still over capacity
        if len(self.sessions) >= self.max_sessions:
            oldest = min(self.sessions.values(), key=lambda s: s.last_accessed)
            self.close_session(oldest.session_id)
