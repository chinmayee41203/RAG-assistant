import streamlit as st
from rag_pipeline import (
    add_documents,
    clear_vector_store,
    get_indexed_sources,
    is_document_indexed,
    stream_rag,
)
from document_processor import process_uploaded_file
import config

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="RAG Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e0e0f0;
    }
    [data-testid="stSidebar"] {
        background: rgba(15,15,30,0.95);
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 1.2rem 0 0.3rem 0;
    }
    .app-header h1 {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .app-header p { color: #64748b; font-size: 0.9rem; }

    /* Welcome card */
    .welcome-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(167,139,250,0.15);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 2rem auto;
        max-width: 600px;
    }
    .welcome-card h2 { color: #a78bfa; font-size: 1.3rem; margin-bottom: 1rem; }
    .welcome-card p { color: #64748b; font-size: 0.9rem; line-height: 1.6; }
    .step-row {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin: 0.8rem 0;
        text-align: left;
    }
    .step-num {
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
    }
    .step-text { color: #94a3b8; font-size: 0.88rem; padding-top: 4px; }

    /* Suggestion chips */
    .chips-label {
        color: #475569;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }

    /* Stats bar */
    .stats-bar {
        display: flex;
        gap: 1.2rem;
        margin-top: 0.6rem;
        padding-top: 0.6rem;
        border-top: 1px solid rgba(255,255,255,0.06);
    }
    .stat-pill {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        color: #64748b;
    }

    /* Source cards */
    .source-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(96,165,250,0.2);
        border-left: 3px solid #60a5fa;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.83rem;
        color: #cbd5e1;
    }
    .source-title {
        color: #60a5fa;
        font-weight: 600;
        margin-bottom: 0.3rem;
        font-size: 0.82rem;
    }

    /* Badges */
    .badge-success {
        background: rgba(52,211,153,0.12);
        color: #34d399;
        border: 1px solid rgba(52,211,153,0.25);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-warning {
        background: rgba(251,191,36,0.12);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.25);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Doc list */
    .doc-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px;
        padding: 0.45rem 0.8rem;
        margin: 0.25rem 0;
        font-size: 0.82rem;
        color: #94a3b8;
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.06); }

    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
    }

    /* Radio buttons */
    [data-testid="stRadio"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(167,139,250,0.25) !important;
        color: #e0e0f0 !important;
        border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(167,139,250,0.6) !important;
        box-shadow: 0 0 0 2px rgba(167,139,250,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = get_indexed_sources()
if "detail_k" not in st.session_state:
    st.session_state.detail_k = 20

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    provider = config.LLM_PROVIDER.upper()
    model = config.OLLAMA_MODEL if config.LLM_PROVIDER == "ollama" else config.OPENAI_MODEL
    st.markdown(
        f"**Provider:** <span class='badge-success'>{provider}</span>&nbsp;&nbsp;"
        f"**Model:** `{model}`",
        unsafe_allow_html=True,
    )

    if config.LLM_PROVIDER == "openai" and not config.OPENAI_API_KEY:
        st.markdown("<span class='badge-warning'>⚠ OPENAI_API_KEY not set</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("## 🎯 Answer Detail Level")

    detail_options = {
        "⚡ Quick  (k=10)":     10,
        "🔍 Deep   (k=20)":     20,
        "📚 Exhaustive (k=30)": 30,
    }
    selected_label = st.radio(
        "detail",
        list(detail_options.keys()),
        index=1,
        label_visibility="collapsed",
    )
    st.session_state.detail_k = detail_options[selected_label]
    st.caption("More chunks = broader coverage, slower response.")

    st.divider()
    st.markdown("## 📂 Upload Documents")

    uploaded_files = st.file_uploader(
        "Supports PDF, TXT, DOCX",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            if is_document_indexed(filename):
                st.info(f"Already indexed: **{filename}**")
                continue

            with st.status(f"Processing **{filename}**...", expanded=True) as status:
                try:
                    st.write("📄 Extracting text...")
                    file_bytes = uploaded_file.read()

                    st.write("✂️ Chunking...")
                    chunks = process_uploaded_file(file_bytes, filename)

                    st.write(f"🔢 Embedding {len(chunks)} chunks on GPU...")
                    add_documents(chunks)

                    st.session_state.indexed_files = get_indexed_sources()
                    status.update(
                        label=f"✅ **{filename}** — {len(chunks)} chunks indexed",
                        state="complete",
                    )
                    st.toast(f"✅ {filename} indexed successfully!", icon="📄")
                except Exception as e:
                    status.update(label=f"❌ Failed: {filename}", state="error")
                    st.toast(f"❌ Failed to index {filename}", icon="🚨")
                    st.error(str(e))

    st.divider()
    st.markdown("## 🗂️ Indexed Documents")

    if st.session_state.indexed_files:
        for doc in st.session_state.indexed_files:
            st.markdown(f"<div class='doc-item'>📄 {doc}</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear DB", use_container_width=True, type="secondary"):
                clear_vector_store()
                st.session_state.indexed_files = []
                st.session_state.messages = []
                st.toast("Database cleared.", icon="🗑️")
                st.rerun()
        with col2:
            if st.button("💬 Clear Chat", use_container_width=True, type="secondary"):
                st.session_state.messages = []
                st.rerun()
    else:
        st.markdown(
            "<div style='color:#475569;font-size:0.83rem;'>No documents indexed yet.</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        "<div style='color:#334155;font-size:0.72rem;text-align:center;'>"
        "RAG 2.0 · LangChain · ChromaDB · Ollama"
        "</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main panel — header
# ---------------------------------------------------------------------------

st.markdown("""
<div class='app-header'>
    <h1>🧠 RAG Knowledge Assistant</h1>
    <p>Ask anything about your uploaded documents — grounded answers with source citations.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Welcome screen (no docs indexed)
# ---------------------------------------------------------------------------

if not st.session_state.indexed_files:
    st.markdown("""
    <div class='welcome-card'>
        <h2>👋 Welcome! Let's get started.</h2>
        <div class='step-row'>
            <div class='step-num'>1</div>
            <div class='step-text'>Upload your documents (PDF, TXT, or DOCX) using the sidebar on the left.</div>
        </div>
        <div class='step-row'>
            <div class='step-num'>2</div>
            <div class='step-text'>Wait for indexing to complete — this is a one-time step per document.</div>
        </div>
        <div class='step-row'>
            <div class='step-num'>3</div>
            <div class='step-text'>Type your question below and get in-depth answers with source citations.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Suggested questions (shown only when chat is empty)
# ---------------------------------------------------------------------------

SUGGESTIONS = [
    "Give me an overview of the main topics covered in this document.",
    "What are the key concepts explained here?",
    "Summarize the most important points.",
    "What definitions or terminology are introduced?",
    "What examples or case studies are discussed?",
]

if not st.session_state.messages:
    st.markdown("<div class='chips-label'>✨ Try asking</div>", unsafe_allow_html=True)
    cols = st.columns(len(SUGGESTIONS))
    for i, (col, suggestion) in enumerate(zip(cols, SUGGESTIONS)):
        with col:
            if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                st.session_state._pending_question = suggestion
                st.rerun()

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            word_count = len(msg["content"].split())
            chunk_count = len(msg.get("sources", []))
            st.markdown(
                f"<div class='stats-bar'>"
                f"<span class='stat-pill'>📝 {word_count} words</span>"
                f"<span class='stat-pill'>🔍 {chunk_count} sources</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if msg.get("sources"):
                with st.expander(f"📚 View Sources ({len(msg['sources'])} references)", expanded=False):
                    for src in msg["sources"]:
                        page_info = f" · Page {src['page']}" if src.get("page") else ""
                        st.markdown(
                            f"<div class='source-card'>"
                            f"<div class='source-title'>📄 {src['source']}{page_info}</div>"
                            f"{src['snippet']}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

# ---------------------------------------------------------------------------
# Handle pending suggestion click
# ---------------------------------------------------------------------------

pending = st.session_state.pop("_pending_question", None)

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

question = st.chat_input("Ask a question about your documents...") or pending

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        answer_placeholder = st.empty()
        full_answer = ""
        sources = []

        try:
            for event in stream_rag(question, k=st.session_state.detail_k):
                if event["type"] == "token":
                    full_answer += event["token"]
                    answer_placeholder.markdown(full_answer + "▌")
                elif event["type"] == "sources":
                    sources = event["sources"]
            answer_placeholder.markdown(full_answer)
        except Exception as e:
            full_answer = f"An error occurred: {e}"
            answer_placeholder.markdown(full_answer)

        word_count = len(full_answer.split())
        st.markdown(
            f"<div class='stats-bar'>"
            f"<span class='stat-pill'>📝 {word_count} words</span>"
            f"<span class='stat-pill'>🔍 {len(sources)} sources</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if sources:
            with st.expander(f"📚 View Sources ({len(sources)} references)", expanded=False):
                for src in sources:
                    page_info = f" · Page {src['page']}" if src.get("page") else ""
                    st.markdown(
                        f"<div class='source-card'>"
                        f"<div class='source-title'>📄 {src['source']}{page_info}</div>"
                        f"{src['snippet']}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_answer,
        "sources": sources,
    })
