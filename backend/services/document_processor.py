import os
import re
from pathlib import Path
from typing import List


class DocumentProcessor:
    """Handles text extraction and chunking from various file types."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str, filename: str) -> List[str]:
        """Process a file and return a list of text chunks."""
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif ext in self._text_extensions():
            text = self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        if not text.strip():
            raise ValueError(f"No text content could be extracted from '{filename}'")

        chunks = self._chunk_text(text, filename)
        return chunks

    def _text_extensions(self):
        return {
            ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx",
            ".java", ".cpp", ".c", ".h", ".hpp", ".cs", ".go",
            ".rs", ".rb", ".php", ".html", ".css", ".json",
            ".yaml", ".yml", ".xml", ".sh", ".bash", ".sql",
            ".r", ".swift", ".kt", ".scala", ".vue", ".svelte",
        }

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file with page markers."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            pages_text = []
            for page_num, page in enumerate(doc):
                page_text = page.get_text("text")
                if page_text.strip():
                    pages_text.append(f"[Page {page_num + 1}]\n{page_text}")
            doc.close()
            return "\n\n".join(pages_text)
        except ImportError:
            raise ImportError("PyMuPDF (fitz) is not installed. Run: pip install pymupdf")
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF: {str(e)}")

    def _extract_text(self, file_path: str) -> str:
        """Extract text from a plain text / code file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {str(e)}")

    def _chunk_text(self, text: str, filename: str) -> List[str]:
        """Split text into overlapping chunks for better retrieval."""
        # Normalize whitespace
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        # Try to split by paragraphs first
        paragraphs = re.split(r"\n\n+", text)

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If a single paragraph exceeds chunk size, split by sentence
            if len(para) > self.chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                        current_chunk = (current_chunk + " " + sentence).strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        # Handle sentences longer than chunk_size
                        if len(sentence) > self.chunk_size:
                            words = sentence.split()
                            temp = ""
                            for word in words:
                                if len(temp) + len(word) + 1 <= self.chunk_size:
                                    temp = (temp + " " + word).strip()
                                else:
                                    if temp:
                                        chunks.append(temp)
                                    temp = word
                            current_chunk = temp
                        else:
                            current_chunk = sentence
            else:
                if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                    current_chunk = (current_chunk + "\n\n" + para).strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        # Add overlap: prepend the last N chars of the previous chunk
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0 and self.chunk_overlap > 0:
                prev_tail = chunks[i - 1][-self.chunk_overlap:]
                chunk = prev_tail + "\n" + chunk
            overlapped_chunks.append(chunk.strip())

        return [c for c in overlapped_chunks if len(c.strip()) > 30]
