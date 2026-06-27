import json
import re
from typing import List, Dict, Any, Generator

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import config

COLLECTION_NAME = "rag_documents"

# ---------------------------------------------------------------------------
# Singletons — one client and one embedding model for the whole process
# ---------------------------------------------------------------------------

_embeddings = None
_chroma_client = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={"device": "cuda"},
            encode_kwargs={"normalize_embeddings": True, "batch_size": 128},
        )
    return _embeddings


def _get_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    return _chroma_client


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------

def get_vector_store() -> Chroma:
    return Chroma(
        client=_get_client(),
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
    )


def get_indexed_sources() -> List[str]:
    store = get_vector_store()
    results = store.get(include=["metadatas"])
    sources = {m.get("source", "") for m in results["metadatas"] if m.get("source")}
    return sorted(sources)


def is_document_indexed(filename: str) -> bool:
    return filename in get_indexed_sources()


def add_documents(chunks: List[Document]) -> int:
    if not chunks:
        return 0
    store = get_vector_store()
    store.add_documents(chunks)
    return len(chunks)


def clear_vector_store() -> None:
    try:
        _get_client().delete_collection(COLLECTION_NAME)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def get_llm():
    if config.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.2,
        )
    elif config.LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.GROQ_MODEL,
            temperature=0.2,
        )
    else:
        from langchain_community.llms import Ollama
        return Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            temperature=0.2,
        )


# ---------------------------------------------------------------------------
# RAG chain
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a knowledgeable assistant that answers questions thoroughly and in depth based strictly on the provided context documents.

Guidelines:
- Answer only from the context below. Do not use outside knowledge.
- If the answer is not in the context, say "I couldn't find relevant information in the uploaded documents."
- Extract and present ALL relevant information from the context that relates to the question — do not leave out details.
- Structure your answer clearly using headings, bullet points, or numbered lists where appropriate.
- Cover every angle of the topic found in the context: definitions, explanations, examples, exceptions, and related concepts.
- Be thorough and informative, not brief. A longer, well-structured answer is preferred over a short one.
- Where relevant, mention which document or page the information comes from.

Context:
{context}
"""

def _format_context(docs: List[Document]) -> str:
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "")
        header = f"[{source}" + (f", page {page}" if page else "") + "]"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def retrieve_docs(question: str, k: int = 20) -> List[Document]:
    store = get_vector_store()
    retriever = store.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(question)


def build_chain(source_docs: List[Document]):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])
    llm = get_llm()
    return (
        {"context": lambda _: _format_context(source_docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def format_sources(source_docs: List[Document]) -> List[Dict[str, Any]]:
    sources = []
    seen = set()
    for doc in source_docs:
        key = (doc.metadata.get("source"), doc.metadata.get("page"), doc.metadata.get("chunk_index"))
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", ""),
                "snippet": doc.page_content[:300].strip(),
            })
    return sources


def query_rag(question: str, k: int = 20) -> Dict[str, Any]:
    source_docs = retrieve_docs(question, k)
    if not source_docs:
        return {
            "answer": "I couldn't find relevant information in the uploaded documents.",
            "sources": [],
        }
    chain = build_chain(source_docs)
    answer = chain.invoke(question)
    return {"answer": answer, "sources": format_sources(source_docs)}


def stream_rag(question: str, k: int = 20) -> Generator[Dict[str, Any], None, None]:
    source_docs = retrieve_docs(question, k)
    if not source_docs:
        yield {"type": "token", "token": "I couldn't find relevant information in the uploaded documents."}
        yield {"type": "sources", "sources": []}
        return
    chain = build_chain(source_docs)
    for chunk in chain.stream(question):
        yield {"type": "token", "token": chunk}
    yield {"type": "sources", "sources": format_sources(source_docs)}


def _default_suggestions(filename: str) -> List[str]:
    return [
        f"What are the main topics covered in {filename}?",
        "What are the key concepts explained in this document?",
        "What examples or case studies are discussed?",
        "What definitions or terminology are introduced?",
        "What are the most important takeaways from this document?",
    ]


def generate_suggestions(chunks: List[Document], filename: str) -> List[str]:
    if not chunks:
        return _default_suggestions(filename)

    sample = "\n\n".join(c.page_content for c in chunks[:3])[:3000]
    prompt = (
        f'You are given content from a document called "{filename}".\n'
        f'Generate exactly 5 specific questions a reader might ask about this content.\n'
        f'Requirements:\n'
        f'- Questions must be specific to the actual content shown, not generic\n'
        f'- Vary the types: definitions, explanations, comparisons, examples, processes\n'
        f'- Make questions natural and conversational\n'
        f'- Output ONLY a valid JSON array of 5 strings, no other text, no markdown\n\n'
        f'Content:\n{sample}\n\n'
        f'JSON array:'
    )
    try:
        llm = get_llm()
        if config.LLM_PROVIDER in ("openai", "groq"):
            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            text = response.content
        else:
            text = llm.invoke(prompt)
        match = re.search(r'\[[\s\S]*?\]', text)
        if match:
            questions = json.loads(match.group())
            return [str(q) for q in questions if q][:5]
    except Exception:
        pass
    return _default_suggestions(filename)
