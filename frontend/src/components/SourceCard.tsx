"use client";
import { useState } from "react";
import { ChevronDown, ChevronUp, FileText } from "lucide-react";
import { Source } from "@/types";

interface Props {
  sources: Source[];
}

export default function SourceCard({ sources }: Props) {
  const [open, setOpen] = useState(false);
  if (!sources.length) return null;

  return (
    <div className="mt-3 border border-slate-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-50 hover:bg-slate-100 transition-colors text-sm font-medium text-slate-600"
      >
        <span className="flex items-center gap-2">
          <FileText size={14} className="text-violet-500" />
          {sources.length} source{sources.length > 1 ? "s" : ""} referenced
        </span>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {open && (
        <div className="divide-y divide-slate-100">
          {sources.map((src, i) => (
            <div key={i} className="px-4 py-3 bg-white">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-violet-600 truncate">
                  {src.source}
                </span>
                {src.page && (
                  <span className="text-xs text-slate-400 shrink-0">· page {src.page}</span>
                )}
              </div>
              <p className="text-xs text-slate-500 leading-relaxed line-clamp-3">
                {src.snippet}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
