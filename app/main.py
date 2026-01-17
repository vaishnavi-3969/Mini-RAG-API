from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv
import uuid
import requests

from app.db import supabase
from app.chunking import chunk_text
from app.embeddings import embed_text

load_dotenv()

app = FastAPI(title="Mini RAG API")


# ----------------------------
# Ollama LLM Call
# ----------------------------
def call_llm(context: str, question: str):
    prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",  # or "gemma:2b"
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    return response.json()["response"]


# ----------------------------
# Upload Document
# ----------------------------
@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith((".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only .txt or .md files allowed")

    content = (await file.read()).decode("utf-8", errors="ignore")

    doc_id = str(uuid.uuid4())

    supabase.table("documents").insert({
        "id": doc_id,
        "filename": file.filename
    }).execute()

    chunks = chunk_text(content)

    for chunk in chunks:
        embedding = embed_text(chunk)

        supabase.table("document_chunks").insert({
            "document_id": doc_id,
            "content": chunk,
            "embedding": embedding
        }).execute()

    return {
        "id": doc_id,
        "filename": file.filename,
        "chunk_count": len(chunks)
    }


# ----------------------------
# List Documents
# ----------------------------
@app.get("/documents")
def list_documents():
    res = supabase.table("documents").select("*").execute()
    return {"documents": res.data}


# ----------------------------
# Query (RAG)
# ----------------------------
@app.post("/query")
def query_docs(payload: dict):
    question = payload.get("question")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    q_embedding = embed_text(question)

    res = supabase.rpc(
        "match_chunks",
        {
            "query_embedding": q_embedding,
            "match_count": 5
        }
    ).execute()

    chunks = res.data or []

    if not chunks:
        return {
            "answer": "No relevant information found.",
            "sources": []
        }

    context = "\n\n".join(chunk["content"] for chunk in chunks)

    answer = call_llm(context, question)

    return {
        "answer": answer,
        "sources": chunks
    }
