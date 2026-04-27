import hashlib
from typing import List, Dict, Any
from pathlib import Path


class VectorStoreService:
    """Manages document embeddings and similarity search using ChromaDB."""

    def __init__(self, persist_dir: str = "./chroma_db"):
        self._init_chroma(persist_dir)
        self._init_embeddings()

    def _init_chroma(self, persist_dir: str):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(
                name="rag_documents",
                metadata={"hnsw:space": "cosine"}
            )
            print(f"[OK] ChromaDB initialized - {self.collection.count()} chunks loaded.")
        except ImportError:
            raise ImportError("chromadb is not installed. Run: pip install chromadb")

    def _init_embeddings(self):
        try:
            from sentence_transformers import SentenceTransformer
            print("[INFO] Loading embedding model (first run may take a minute)...")
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[OK] Embedding model loaded.")
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. Run: pip install sentence-transformers"
            )

    def _embed(self, texts: List[str]) -> List[List[float]]:
        return self.embed_model.encode(texts, show_progress_bar=False).tolist()

    def add_documents(self, chunks: List[str], filename: str):
        """Embed and store document chunks."""
        if not chunks:
            return

        embeddings = self._embed(chunks)
        ids, metadatas = [], []

        for i, chunk in enumerate(chunks):
            uid = hashlib.sha256(f"{filename}::{i}::{chunk[:80]}".encode()).hexdigest()[:32]
            ids.append(uid)
            metadatas.append({"filename": filename, "chunk_index": i, "total_chunks": len(chunks)})

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        print(f"[OK] Indexed {len(chunks)} chunks from '{filename}'")

    def search(self, query: str, n_results: int = 6) -> List[Dict[str, Any]]:
        """Find the most relevant chunks for a query."""
        total = self.collection.count()
        if total == 0:
            return []

        n = min(n_results, total)
        query_embedding = self._embed([query])

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            similarity = round(1 - dist, 4)
            if similarity > 0.15:   # relevance threshold
                hits.append({
                    "content": doc,
                    "filename": meta["filename"],
                    "chunk_index": meta["chunk_index"],
                    "total_chunks": meta["total_chunks"],
                    "score": similarity,
                })

        return sorted(hits, key=lambda x: x["score"], reverse=True)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Return metadata about every unique document."""
        results = self.collection.get(include=["metadatas"])
        seen: Dict[str, int] = {}
        for meta in results["metadatas"]:
            fname = meta["filename"]
            seen[fname] = meta.get("total_chunks", seen.get(fname, 0))

        return [{"filename": k, "chunks": v} for k, v in seen.items()]

    def delete_document(self, filename: str):
        """Remove all chunks belonging to a document."""
        results = self.collection.get(where={"filename": filename}, include=[])
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            print(f"[DEL] Deleted {len(results['ids'])} chunks for '{filename}'")
