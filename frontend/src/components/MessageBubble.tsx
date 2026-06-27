"use client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "@/types";
import SourceCard from "./SourceCard";

interface Props {
  message: Message;
  isStreaming?: boolean;
}

export default function MessageBubble({ message, isStreaming }: Props) {
  const isUser = message.role === "user";
  const wordCount = message.content.split(/\s+/).filter(Boolean).length;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 fade-up`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center text-white text-xs font-bold mr-3 shrink-0 mt-1">
          AI
        </div>
      )}

      <div className={`max-w-[78%] ${isUser ? "max-w-[65%]" : ""}`}>
        {isUser ? (
          <div className="bg-violet-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm shadow-sm text-sm leading-relaxed">
            {message.content}
          </div>
        ) : (
          <div className="bg-white border border-slate-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm">
            {isStreaming && !message.content ? (
              <div className="flex items-center gap-2.5 py-1">
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span className="text-xs font-semibold tracking-widest text-violet-500 uppercase">
                  Retrieving
                </span>
              </div>
            ) : (
              <div className="prose text-sm text-slate-800 max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
                {isStreaming && <span className="cursor" />}
              </div>
            )}

            {!isStreaming && (
              <>
                <div className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-100">
                  <span className="text-xs text-slate-400">{wordCount} words</span>
                  {message.sources && message.sources.length > 0 && (
                    <span className="text-xs text-slate-400">{message.sources.length} sources</span>
                  )}
                </div>
                {message.sources && <SourceCard sources={message.sources} />}
              </>
            )}
          </div>
        )}

        <div className={`text-xs text-slate-400 mt-1 ${isUser ? "text-right" : ""}`}>
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-xs font-bold ml-3 shrink-0 mt-1">
          U
        </div>
      )}
    </div>
  );
}
