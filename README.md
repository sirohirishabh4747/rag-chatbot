# 🧠 DocuMind — RAG Knowledge Chatbot

A full-stack, production-ready RAG (Retrieval-Augmented Generation) chatbot that lets you **chat with your documents**. Upload any PDF, code file, or text, and ask questions in plain English. The AI answers based strictly on your documents and always cites its sources.

---

## ✨ Features

- 📄 **Multi-format support** — PDF, Python, JavaScript, Java, C++, Markdown, JSON, YAML, SQL, and 30+ more
- 🔍 **Semantic search** — Finds relevant sections even with different wording  
- 🏷️ **Source citations** — Every answer shows which document it came from + relevance score
- 💬 **Conversation memory** — Remembers the last 8 turns of your chat
- 🗂️ **Persistent knowledge base** — Documents survive server restarts (ChromaDB)
- 🌙 **Beautiful dark UI** — ChatGPT-like interface with drag-and-drop upload
- ⚡ **Fast responses** — Powered by Groq's LLaMA 3.1 (free tier available)

---

## 🗂️ Project Structure

```
rag-chatbot/
├── backend/
│   ├── main.py                    # FastAPI app & API routes
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Your API keys (create this)
│   ├── uploads/                   # Uploaded files stored here
│   ├── chroma_db/                 # Vector database (auto-created)
│   └── services/
│       ├── document_processor.py  # PDF/text extraction & chunking
│       ├── vector_store.py        # ChromaDB + embeddings
│       └── rag_engine.py          # Groq LLM + RAG logic
├── frontend/
│   └── index.html                 # Complete UI (HTML + CSS + JS)
├── .env.example                   # Template for environment variables
├── start.sh                       # Linux/Mac one-click start
├── start.bat                      # Windows one-click start
└── README.md                      # This file
```

---

## 🆓 How to Get a FREE API Key

### Groq (Recommended — Fast & Generous Free Tier)

1. Go to **https://console.groq.com**
2. Click **"Sign Up"** (free, no credit card needed)
3. Go to **API Keys** in the left menu
4. Click **"Create API Key"**
5. Copy the key — it looks like `gsk_xxxxxxxxxxxxxxxxxxxx`

**Free tier limits:** ~14,400 requests/day, 6000 tokens/min — more than enough for personal use.

### Available Free Models on Groq

| Model | Speed | Best For |
|-------|-------|----------|
| `llama-3.1-8b-instant` | ⚡ Fastest | General Q&A (DEFAULT) |
| `llama-3.1-70b-versatile` | Slower | Complex reasoning |
| `mixtral-8x7b-32768` | Fast | Long documents |
| `gemma2-9b-it` | Fast | Concise answers |

---

## 🚀 Running Locally — Step by Step

### Prerequisites

- **Python 3.9 or higher** — https://www.python.org/downloads/
- **Git** (optional) — https://git-scm.com/

---

### Step 1 — Extract the ZIP

Extract `rag-chatbot.zip` to any folder on your computer.

---

### Step 2 — Create Your .env File

```bash
# Navigate to the project
cd rag-chatbot

# Copy the example file
cp .env.example backend/.env      # Mac/Linux
copy .env.example backend\.env    # Windows
```

Open `backend/.env` in any text editor and add your key:
```env
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

---

### Step 3A — Quick Start (Recommended)

**Mac / Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
Double-click `start.bat`

---

### Step 3B — Manual Setup

```bash
# Go to backend folder
cd rag-chatbot/backend

# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows

# Install all dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Step 4 — Open the App

Open your browser and go to:
```
http://localhost:8000
```

You'll see the DocuMind chat interface! 🎉

---

## 📖 How to Use

1. **Upload documents** — Drag & drop or click the upload area in the left sidebar
2. **Wait for indexing** — A toast notification confirms the upload (usually 2–10 seconds)
3. **Ask questions** — Type in the chat box and press Enter
4. **See sources** — Each AI answer shows source cards with the document name and relevance %
5. **Delete documents** — Click the ✕ button on any document in the sidebar

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the frontend |
| POST | `/api/upload` | Upload & index a file |
| POST | `/api/chat` | Send a message |
| GET | `/api/documents` | List all documents |
| DELETE | `/api/documents/{filename}` | Delete a document |
| GET | `/api/health` | Health check |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `GROQ_API_KEY not set` | Check backend/.env file exists with your key |
| `Port 8000 in use` | Run `uvicorn main:app --port 8001` |
| `PDF extraction failed` | Ensure pymupdf is installed: `pip install pymupdf` |
| `Slow first start` | Normal! The embedding model (~90MB) downloads once |
| `No answer from docs` | Check if documents are uploaded (left sidebar shows count) |
| `Frontend not loading` | Access via `http://localhost:8000`, not by opening the HTML file directly |

---

## 🧪 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python) |
| **LLM** | Groq API (LLaMA 3.1) — Free |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) — Free, local |
| **Vector DB** | ChromaDB — Free, local, persistent |
| **PDF Parser** | PyMuPDF (fitz) |
| **Frontend** | Vanilla HTML + CSS + JavaScript |

---

## 📝 License

MIT License — Free to use, modify, and distribute.
