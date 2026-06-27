export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: Date;
}

export interface Source {
  source: string;
  page: number | string;
  snippet: string;
}

export interface UploadResult {
  status: "indexed" | "already_indexed";
  filename: string;
  chunks: number;
  suggestions: string[];
}
