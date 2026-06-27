import { Source, UploadResult } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getSources(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/sources`);
  const data = await res.json();
  return data.sources as string[];
}

export async function clearSources(): Promise<void> {
  await fetch(`${API_BASE}/api/sources`, { method: "DELETE" });
}

export async function uploadFile(file: File): Promise<UploadResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export type StreamEvent =
  | { type: "token"; token: string }
  | { type: "sources"; sources: Source[] }
  | { type: "error"; message: string };

export async function* streamChat(
  question: string,
  k: number
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, k }),
  });

  if (!res.ok || !res.body) throw new Error("Chat request failed");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const raw = line.slice(6).trim();
      if (raw === "[DONE]") return;
      try {
        yield JSON.parse(raw) as StreamEvent;
      } catch {}
    }
  }
}
