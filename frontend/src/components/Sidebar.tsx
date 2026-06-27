"use client";
import { useRef, useState } from "react";
import {
  Upload, FileText, Trash2, MessageSquareX,
  CheckCircle2, AlertCircle, Loader2, BookOpen,
} from "lucide-react";
import { uploadFile, clearSources } from "@/lib/api";
import { UploadResult } from "@/types";

interface Props {
  indexedFiles: string[];
  detailK: number;
  onDetailChange: (k: number) => void;
  onUploadSuccess: (result: UploadResult) => void;
  onClearDB: () => void;
  onClearChat: () => void;
}

interface FileStatus {
  name: string;
  state: "uploading" | "done" | "duplicate" | "error";
  message?: string;
}

const DETAIL_OPTIONS = [
  { label: "⚡ Quick", desc: "k=10", k: 10 },
  { label: "🔍 Deep", desc: "k=20", k: 20 },
  { label: "📚 Exhaustive", desc: "k=30", k: 30 },
];

export default function Sidebar({ indexedFiles, detailK, onDetailChange, onUploadSuccess, onClearDB, onClearChat }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [fileStatuses, setFileStatuses] = useState<FileStatus[]>([]);

  const handleFiles = async (files: FileList | null) => {
    if (!files) return;
    const arr = Array.from(files);

    for (const file of arr) {
      setFileStatuses((prev) => [...prev.filter((f) => f.name !== file.name), { name: file.name, state: "uploading" }]);
      try {
        const result = await uploadFile(file);
        setFileStatuses((prev) =>
          prev.map((f) => f.name === file.name
            ? { name: file.name, state: result.status === "already_indexed" ? "duplicate" : "done", message: result.status === "already_indexed" ? "Already indexed" : `${result.chunks} chunks` }
            : f
          )
        );
        onUploadSuccess(result);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Upload failed";
        setFileStatuses((prev) => prev.map((f) => f.name === file.name ? { name: file.name, state: "error", message: msg } : f));
      }
    }
  };

  const handleClearDB = async () => {
    await clearSources();
    setFileStatuses([]);
    onClearDB();
  };

  return (
    <aside className="w-72 h-full bg-white border-r border-slate-200 flex flex-col overflow-hidden shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center">
            <BookOpen size={16} className="text-white" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-800">RAG Assistant</div>
            <div className="text-xs text-slate-400">Knowledge Q&A</div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">

        {/* Upload */}
        <div>
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Upload Documents</div>
          <div
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
            className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center cursor-pointer hover:border-violet-400 hover:bg-violet-50 transition-all duration-150 group"
          >
            <Upload size={20} className="mx-auto mb-2 text-slate-300 group-hover:text-violet-500 transition-colors" />
            <p className="text-xs text-slate-500 group-hover:text-violet-600 transition-colors">
              Click or drag files here
            </p>
            <p className="text-xs text-slate-400 mt-1">PDF · TXT · DOCX</p>
          </div>
          <input ref={fileRef} type="file" multiple accept=".pdf,.txt,.docx" className="hidden" onChange={(e) => handleFiles(e.target.files)} />
        </div>

        {/* File statuses */}
        {fileStatuses.length > 0 && (
          <div className="space-y-1.5">
            {fileStatuses.map((f) => (
              <div key={f.name} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-100">
                {f.state === "uploading" && <Loader2 size={14} className="text-violet-500 animate-spin shrink-0" />}
                {f.state === "done" && <CheckCircle2 size={14} className="text-green-500 shrink-0" />}
                {f.state === "duplicate" && <CheckCircle2 size={14} className="text-slate-400 shrink-0" />}
                {f.state === "error" && <AlertCircle size={14} className="text-red-400 shrink-0" />}
                <div className="min-w-0">
                  <p className="text-xs font-medium text-slate-700 truncate">{f.name}</p>
                  {f.message && <p className="text-xs text-slate-400">{f.message}</p>}
                  {f.state === "uploading" && <p className="text-xs text-violet-500">Processing…</p>}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Indexed docs */}
        {indexedFiles.length > 0 && (
          <div>
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
              Indexed ({indexedFiles.length})
            </div>
            <div className="space-y-1">
              {indexedFiles.map((f) => (
                <div key={f} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-100">
                  <FileText size={13} className="text-violet-400 shrink-0" />
                  <span className="text-xs text-slate-600 truncate">{f}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detail level */}
        <div>
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Answer Coverage</div>
          <div className="space-y-1">
            {DETAIL_OPTIONS.map((opt) => (
              <button
                key={opt.k}
                onClick={() => onDetailChange(opt.k)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-all ${
                  detailK === opt.k
                    ? "bg-violet-600 text-white shadow-sm"
                    : "bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-100"
                }`}
              >
                <span>{opt.label}</span>
                <span className={`text-xs ${detailK === opt.k ? "text-violet-200" : "text-slate-400"}`}>{opt.desc}</span>
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-2">More chunks = deeper answers, slower response.</p>
        </div>
      </div>

      {/* Bottom actions */}
      <div className="px-4 py-4 border-t border-slate-100 space-y-2">
        <button
          onClick={onClearChat}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-600 hover:bg-slate-100 border border-slate-200 transition-colors"
        >
          <MessageSquareX size={14} />
          Clear Chat
        </button>
        <button
          onClick={handleClearDB}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm text-red-500 hover:bg-red-50 border border-red-100 transition-colors"
        >
          <Trash2 size={14} />
          Clear All Documents
        </button>
      </div>
    </aside>
  );
}
