export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  model: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  charts: PlotlyChartData[];
  timestamp: Date;
  isStreaming: boolean;
  toolStatus?: string;
  tokenUsage?: TokenUsage;
}

export interface PlotlyChartData {
  data: any[];
  layout: any;
  frames?: any[];
}

export interface FileInfo {
  file_id: string;
  filename: string;
  source_tool: string;
  application: string;
  game_name: string;
  rows: number;
  duration_seconds: number;
  columns_available: number;
  columns_na: number;
  profile: Record<string, any>;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  file_count: number;
  files: { file_id: string; name: string; application: string }[];
}

export type WSMessageType =
  | { type: "text_delta"; content: string }
  | { type: "chart"; data: PlotlyChartData }
  | { type: "tool_status"; content: string }
  | { type: "token_usage"; input_tokens: number; output_tokens: number; model: string }
  | { type: "message_end"; charts?: PlotlyChartData[] }
  | { type: "error"; content: string };
