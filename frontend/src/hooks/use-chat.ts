"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import type { ChatMessage, PlotlyChartData, WSMessageType } from "@/lib/types";
import { generateId } from "@/lib/utils";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

/** Replace a message in the array by id with a shallow copy of the ref. */
function updateMsgById(
  prev: ChatMessage[],
  ref: ChatMessage | null
): ChatMessage[] {
  if (!ref) return prev;
  return prev.map((m) => (m.id === ref.id ? { ...ref } : m));
}

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const currentMsgRef = useRef<ChatMessage | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!sessionId) return;

    const ws = new WebSocket(`${WS_URL}/ws/chat/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      reconnectTimerRef.current = setTimeout(() => {
        connect();
      }, 2000);
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    ws.onmessage = (event) => {
      try {
        const data: WSMessageType = JSON.parse(event.data);

        switch (data.type) {
          case "text_delta": {
            if (!currentMsgRef.current) {
              const newMsg: ChatMessage = {
                id: generateId(),
                role: "assistant",
                content: "",
                charts: [],
                timestamp: new Date(),
                isStreaming: true,
              };
              currentMsgRef.current = newMsg;
              setMessages((prev) => [...prev, newMsg]);
            }
            currentMsgRef.current.content += data.content;
            setMessages((prev) => updateMsgById(prev, currentMsgRef.current));
            break;
          }

          case "chart": {
            if (!currentMsgRef.current) {
              const newMsg: ChatMessage = {
                id: generateId(),
                role: "assistant",
                content: "",
                charts: [],
                timestamp: new Date(),
                isStreaming: true,
              };
              currentMsgRef.current = newMsg;
              setMessages((prev) => [...prev, newMsg]);
            }
            const chartData = data.data as PlotlyChartData;
            currentMsgRef.current.charts = [
              ...currentMsgRef.current.charts,
              chartData,
            ];
            setMessages((prev) => updateMsgById(prev, currentMsgRef.current));
            break;
          }

          case "tool_status": {
            if (currentMsgRef.current) {
              currentMsgRef.current.toolStatus = data.content;
              setMessages((prev) => updateMsgById(prev, currentMsgRef.current));
            }
            break;
          }

          case "token_usage": {
            if (currentMsgRef.current) {
              currentMsgRef.current.tokenUsage = {
                input_tokens: data.input_tokens,
                output_tokens: data.output_tokens,
                model: data.model,
              };
              setMessages((prev) => updateMsgById(prev, currentMsgRef.current));
            }
            break;
          }

          case "message_end": {
            if (currentMsgRef.current) {
              currentMsgRef.current.isStreaming = false;
              currentMsgRef.current.toolStatus = undefined;

              // Extract token_usage bundled in message_end
              const endUsage = (data as any).token_usage as
                | { input_tokens: number; output_tokens: number; model: string }
                | undefined;
              if (endUsage) {
                currentMsgRef.current.tokenUsage = endUsage;
              }

              setMessages((prev) => updateMsgById(prev, currentMsgRef.current));
            }

            // Add charts as separate subsequent bubbles
            const endCharts = (data as any).charts as PlotlyChartData[] | undefined;
            if (endCharts && endCharts.length > 0) {
              const chartMessages: ChatMessage[] = endCharts.map((chart) => ({
                id: generateId(),
                role: "assistant" as const,
                content: "",
                charts: [chart],
                timestamp: new Date(),
                isStreaming: false,
              }));
              setMessages((prev) => [...prev, ...chartMessages]);
            }

            currentMsgRef.current = null;
            setIsLoading(false);
            break;
          }

          case "error": {
            currentMsgRef.current = null;
            setIsLoading(false);
            break;
          }
        }
      } catch (err) {
        console.error("[WS] message handler error:", err);
      }
    };
  }, [sessionId]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

      const userMsg: ChatMessage = {
        id: generateId(),
        role: "user",
        content,
        charts: [],
        timestamp: new Date(),
        isStreaming: false,
      };

      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      wsRef.current.send(JSON.stringify({ message: content }));
    },
    []
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, sendMessage, isConnected, isLoading, clearMessages };
}
