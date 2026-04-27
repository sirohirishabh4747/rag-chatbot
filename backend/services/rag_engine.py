import os
from typing import List, Dict, Any
from services.vector_store import VectorStoreService


class RAGEngine:
    """Combines retrieval and generation to answer user questions."""

    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self._init_llm()

    def _init_llm(self):
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY environment variable is not set.\n"
                "Get your free key at https://console.groq.com"
            )
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            self.model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
            print(f"[OK] Groq LLM ready - model: {self.model}")
        except ImportError:
            raise ImportError("groq is not installed. Run: pip install groq")

    async def query(self, question: str, conversation_history: List[Dict] = []) -> Dict[str, Any]:
        """Retrieve relevant context and generate a grounded answer."""
        relevant_chunks = self.vector_store.search(question, n_results=6)
        has_context = bool(relevant_chunks)

        if has_context:
            context_str = self._build_context_str(relevant_chunks)
            sources = self._deduplicate_sources(relevant_chunks)
        else:
            context_str = "No documents are in the knowledge base yet."
            sources = []

        messages = self._build_messages(question, context_str, conversation_history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=2048,
        )

        answer = response.choices[0].message.content.strip()

        return {
            "answer": answer,
            "sources": sources,
            "has_context": has_context,
            "chunks_used": len(relevant_chunks),
        }

    # ------------------------------------------------------------------ helpers

    def _build_context_str(self, chunks: List[Dict]) -> str:
        parts = []
        for i, chunk in enumerate(chunks, start=1):
            score_pct = round(chunk["score"] * 100, 1)
            parts.append(
                f"--- SOURCE {i}: {chunk['filename']} "
                f"(chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']}, "
                f"relevance: {score_pct}%) ---\n{chunk['content']}"
            )
        return "\n\n".join(parts)

    def _deduplicate_sources(self, chunks: List[Dict]) -> List[Dict]:
        seen: Dict[str, float] = {}
        for c in chunks:
            fname = c["filename"]
            if fname not in seen or c["score"] > seen[fname]:
                seen[fname] = c["score"]

        return [
            {"filename": k, "relevance_pct": round(v * 100, 1)}
            for k, v in sorted(seen.items(), key=lambda x: x[1], reverse=True)
        ]

    def _build_messages(
        self, question: str, context: str, history: List[Dict]
    ) -> List[Dict]:
        system_prompt = f"""You are a knowledgeable AI assistant that answers questions strictly based on the provided document context.

INSTRUCTIONS:
1. Answer ONLY based on the context provided below. Do not make up information.
2. Always mention which document(s) your answer comes from (use the filename shown in the SOURCE headers).
3. If the context does not contain enough information to answer the question, clearly say: "I couldn't find relevant information in the uploaded documents for this question."
4. Format your response clearly. Use bullet points or numbered lists when appropriate.
5. Always respond in English.
6. Be concise yet thorough.

KNOWLEDGE BASE CONTEXT:
{context}
"""

        messages = [{"role": "system", "content": system_prompt}]

        # Include last 8 turns of conversation for continuity
        for turn in history[-8:]:
            if turn.get("role") in ("user", "assistant") and turn.get("content"):
                messages.append({"role": turn["role"], "content": turn["content"]})

        messages.append({"role": "user", "content": question})
        return messages
