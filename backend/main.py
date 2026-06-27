import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import config
from rag_pipeline import (
    add_documents,
    clear_vector_store,
    get_indexed_sources,
    is_document_indexed,
    stream_rag,
    generate_suggestions,
)
from document_processor import process_uploaded_file

app = FastAPI(title="RAG 2.0 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    k: int = 20


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/sources")
def get_sources():
    return {"sources": get_indexed_sources()}


@app.delete("/api/sources")
def delete_sources():
    clear_vector_store()
    return {"status": "cleared"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    allowed = {".pdf", ".txt", ".docx"}
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    if is_document_indexed(filename):
        return {"status": "already_indexed", "filename": filename, "chunks": 0, "suggestions": []}

    file_bytes = await file.read()
    chunks = process_uploaded_file(file_bytes, filename)
    add_documents(chunks)
    suggestions = generate_suggestions(chunks, filename)

    return {
        "status": "indexed",
        "filename": filename,
        "chunks": len(chunks),
        "suggestions": suggestions,
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    def generate():
        try:
            for event in stream_rag(request.question, k=request.k):
                yield f"data: {json.dumps(event)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
