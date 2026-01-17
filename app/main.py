from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
import uuid

from app.db import supabase
from app.chunking import chunk_text
from app.embeddings import embed_text

load_dotenv()

app = FastAPI()

@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")

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

@app.post("/query")
def query_docs(payload: dict):
    question = payload["question"]

    q_embedding = embed_text(question)

    res = supabase.rpc("match_chunks", {
        "query_embedding": q_embedding,
        "match_count": 5
    }).execute()

    context = "\n".join([r["content"] for r in res.data])

    from openai import OpenAI
    client = OpenAI()

    answer = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer using only the given context"},
            {"role": "user", "content": f"{context}\n\nQuestion: {question}"}
        ]
    )

    return {
        "answer": answer.choices[0].message.content,
        "sources": res.data
    }
