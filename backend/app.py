from dotenv import load_dotenv
load_dotenv()

import os, json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from rag import VectorStore
from llm_providers import load_llm  # your Ollama-backed loader

DATA_DIR = "data"
INDEX_DIR = "index"

app = FastAPI()

# --- CORS FIRST (so preflight OPTIONS is handled) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # dev: allow all; lock down later
    allow_credentials=True,
    allow_methods=["*"],        # <- this is key (OPTIONS, POST, etc.)
    allow_headers=["*"],
)

# Optional: make OPTIONS on /chat-stream explicitly 204 to silence any frameworks
@app.options("/chat-stream")
def options_chat_stream():
    return Response(status_code=204)

# --- RAG + LLM setup ---
vs = VectorStore(INDEX_DIR)
llm = load_llm()   # returns an object with .stream(messages, temperature)

class ChatRequest(BaseModel):
    query: str
    k: int = 5
    temperature: float = 0.4
    system: Optional[str] = None
    history: List[dict] = []

@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(default=[])):
    os.makedirs(DATA_DIR, exist_ok=True)
    for f in files:
        with open(os.path.join(DATA_DIR, f.filename), "wb") as out:
            out.write(await f.read())
    chunks = vs.ingest_folder(DATA_DIR)
    return {"chunks": chunks}

@app.post("/chat-stream")
async def chat_stream(req: ChatRequest):
    # 1) RAG search
    hits = vs.search(req.query, k=req.k)
    ctx = [f"[Source {i+1}]\n{txt[:1400]}" for i, (txt, _) in enumerate(hits)]

    # 2) Build messages for LLM
    messages = [
        {
            "role": "system",
            "content": req.system or "You are helpful and chatty. Cite sources like [1], [2].",
        }
    ]
    messages += req.history
    messages.append({
        "role": "user",
        "content": "Use only the sources below.\n\n"
                   + "\n\n".join(ctx)
                   + f"\n\nQuestion: {req.query}\nAnswer:"
    })

    # 3) SSE stream generator
    def gen():
        # Send a small META block first (let frontend show sources immediately)
        meta = {"sources": [f"[{i+1}]" for i in range(len(hits))]}
        yield {"event": "meta", "data": json.dumps(meta)}
        # Token stream from model
        for delta in llm.stream(messages, req.temperature):
            yield {"event": "token", "data": delta}
        yield {"event": "done", "data": ""}

    # Explicit SSE headers help some browsers/proxies
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        # Content-Type is set by EventSourceResponse, but keeping here is fine
    }
    return EventSourceResponse(gen(), headers=headers)

# (No need to run uvicorn here; you’re starting it from the terminal)
