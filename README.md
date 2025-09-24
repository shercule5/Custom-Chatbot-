ECHO is on.
# Custom RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot with:
- **Backend:** FastAPI + Vector Search
- **Frontend:** React + Vite
- **LLM:** Ollama (local models, e.g. `mistral`, `llama2`)

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/shercule5/Custom-Chatbot-.git
cd Custom-Chatbot-

2. Backend
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app:app --reload


Backend will start at: http://127.0.0.1:8000

3. Frontend
cd frontend
npm install
npm run dev


Frontend will start at: http://localhost:5173

4. Ollama

Make sure Ollama
 is installed. Pull and run a model:

ollama pull mistral


✅ Once everything is running:

Backend → http://127.0.0.1:8000/docs

Frontend → http://localhost:5173

Open the UI, type a question, and start chatting 🎉


