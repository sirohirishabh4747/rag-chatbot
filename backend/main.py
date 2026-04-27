from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStoreService
from services.rag_engine import RAGEngine

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize services
doc_processor = DocumentProcessor()
vector_store = VectorStoreService()
rag_engine = RAGEngine(vector_store)

# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []


@app.get("/", response_class=HTMLResponse)
async def root():
    html_file = frontend_path / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse(content="<h1>RAG Chatbot API is running!</h1>", status_code=200)


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    allowed_extensions = {
        '.pdf', '.txt', '.md', '.py', '.js', '.ts', '.java', '.cpp',
        '.c', '.h', '.cs', '.go', '.rs', '.rb', '.php', '.html',
        '.css', '.json', '.yaml', '.yml', '.xml', '.sh', '.sql',
        '.r', '.swift', '.kt', '.scala'
    }

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' is not supported. Supported: {', '.join(sorted(allowed_extensions))}"
        )

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunks = doc_processor.process_file(str(file_path), file.filename)
        vector_store.add_documents(chunks, file.filename)
        return {
            "success": True,
            "message": f"'{file.filename}' uploaded and indexed successfully",
            "chunks_indexed": len(chunks),
            "filename": file.filename
        }
    except Exception as e:
        # Cleanup on failure
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        response = await rag_engine.query(request.message, request.conversation_history)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/api/documents")
async def get_documents():
    try:
        docs = vector_store.get_all_documents()
        return {"documents": docs, "count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    try:
        vector_store.delete_document(filename)
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
        return {"success": True, "message": f"'{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    doc_count = len(vector_store.get_all_documents())
    return {
        "status": "healthy",
        "documents_indexed": doc_count,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
