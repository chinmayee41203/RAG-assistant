"use client";
import { useEffect, useRef, useState } from "react";
import { Send, Brain } from "lucide-react";
import { getSources } from "@/lib/api";
import { streamChat } from "@/lib/api";
import { Message, UploadResult } from "@/types";
import Sidebar from "@/components/Sidebar";
import MessageBubble from "@/components/MessageBubble";
import SuggestionChips from "@/components/SuggestionChips";

function uid() {
  return Math.random().toString(36).slice(2);
}

const EMPTY_SUGGESTIONS = [
  "What are the main topics covered in this document?",
  "What key concepts are introduced here?",
  "Summarize the most important points.",
  "What definitions or terminology are used?",
  "What examples are discussed?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [indexedFiles, setIndexedFiles] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>(EMPTY_SUGGESTIONS);
  const [detailK, setDetailK] = useState(20);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    getSources().then(setIndexedFiles).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleUploadSuccess = (result: UploadResult) => {
    if (result.status === "indexed") {
      setIndexedFiles((prev) => [...new Set([...prev, result.filename])]);
      if (result.suggestions?.length) setSuggestions(result.suggestions);
    }
  };

  const handleClearDB = () => {
    setIndexedFiles([]);
    setMessages([]);
    setSuggestions(EMPTY_SUGGESTIONS);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const submit = async (question: string) => {
    const q = question.trim();
    if (!q || isStreaming) return;
    setInput("");

    const userMsg: Message = { id: uid(), role: "user", content: q, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);

    const assistantId = uid();
    const assistantMsg: Message = { id: assistantId, role: "assistant", content: "", timestamp: new Date() };
    setMessages((prev) => [...prev, assistantMsg]);
    setIsStreaming(true);

    try {
      let fullContent = "";
      for await (const event of streamChat(q, detailK)) {
        if (event.type === "token") {
          fullContent += event.token;
          setMessages((prev) =>
            prev.map((m) => m.id === assistantId ? { ...m, content: fullContent } : m)
          );
        } else if (event.type === "sources") {
          setMessages((prev) =>
            prev.map((m) => m.id === assistantId ? { ...m, sources: event.sources } : m)
          );
        } else if (event.type === "error") {
          setMessages((prev) =>
            prev.map((m) => m.id === assistantId ? { ...m, content: `Error: ${event.message}` } : m)
          );
        }
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Something went wrong.";
      setMessages((prev) =>
        prev.map((m) => m.id === assistantId ? { ...m, content: `Error: ${msg}` } : m)
      );
    } finally {
      setIsStreaming(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit(input);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar
        indexedFiles={indexedFiles}
        detailK={detailK}
        onDetailChange={setDetailK}
        onUploadSuccess={handleUploadSuccess}
        onClearDB={handleClearDB}
        onClearChat={handleClearChat}
      />

      {/* Main panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-violet-100 flex items-center justify-center">
            <Brain size={18} className="text-violet-600" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-800">RAG Knowledge Assistant</h1>
            <p className="text-xs text-slate-400">
              {indexedFiles.length > 0
                ? `${indexedFiles.length} document${indexedFiles.length > 1 ? "s" : ""} indexed · ${detailK} chunks per query`
                : "Upload documents to get started"}
            </p>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 && indexedFiles.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center fade-up">
              <div className="w-16 h-16 rounded-2xl bg-violet-100 flex items-center justify-center mb-4">
                <Brain size={32} className="text-violet-500" />
              </div>
              <h2 className="text-xl font-bold text-slate-700 mb-2">Welcome to RAG Assistant</h2>
              <p className="text-slate-400 text-sm max-w-sm mb-6">
                Upload a PDF, TXT, or DOCX file from the sidebar to get started. You can then ask detailed questions about its content.
              </p>
              <div className="grid grid-cols-3 gap-3 text-xs text-slate-500">
                {["📄 Upload documents", "🔍 Semantic search", "💬 Cited answers"].map((s) => (
                  <div key={s} className="bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-sm">{s}</div>
                ))}
              </div>
            </div>
          )}

          {messages.length === 0 && indexedFiles.length > 0 && (
            <div className="flex flex-col items-center justify-center h-full fade-up">
              <p className="text-slate-400 text-sm mb-6">
                {indexedFiles.length} document{indexedFiles.length > 1 ? "s" : ""} ready. Ask anything below.
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              isStreaming={isStreaming && msg.role === "assistant" && msg.id === messages[messages.length - 1]?.id}
            />
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions + input */}
        <div className="bg-white border-t border-slate-200 shrink-0">
          {messages.length === 0 && indexedFiles.length > 0 && (
            <SuggestionChips suggestions={suggestions} onSelect={(q) => submit(q)} />
          )}

          <div className="px-4 py-3 flex items-end gap-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={indexedFiles.length === 0 ? "Upload a document first…" : "Ask a question… (Enter to send, Shift+Enter for new line)"}
              disabled={indexedFiles.length === 0 || isStreaming}
              rows={1}
              className="flex-1 resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-400 transition-all"
              style={{ maxHeight: "140px", overflowY: "auto" }}
              onInput={(e) => {
                const t = e.currentTarget;
                t.style.height = "auto";
                t.style.height = `${Math.min(t.scrollHeight, 140)}px`;
              }}
            />
            <button
              onClick={() => submit(input)}
              disabled={!input.trim() || isStreaming || indexedFiles.length === 0}
              className="w-10 h-10 rounded-xl bg-violet-600 hover:bg-violet-700 disabled:bg-slate-200 disabled:cursor-not-allowed flex items-center justify-center transition-colors shadow-sm shrink-0"
            >
              <Send size={16} className={input.trim() && !isStreaming ? "text-white" : "text-slate-400"} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
