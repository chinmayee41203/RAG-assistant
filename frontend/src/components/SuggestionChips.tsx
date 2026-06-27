"use client";
import { Sparkles } from "lucide-react";

interface Props {
  suggestions: string[];
  onSelect: (q: string) => void;
}

export default function SuggestionChips({ suggestions, onSelect }: Props) {
  if (!suggestions.length) return null;

  return (
    <div className="px-4 pb-4">
      <div className="flex items-center gap-1.5 mb-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">
        <Sparkles size={12} className="text-violet-400" />
        Suggested questions
      </div>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            className="text-left text-sm px-4 py-2 rounded-full border border-violet-200 bg-violet-50 text-violet-700 hover:bg-violet-100 hover:border-violet-300 transition-all duration-150 shadow-sm hover:shadow-md fade-up"
            style={{ animationDelay: `${i * 40}ms` }}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
