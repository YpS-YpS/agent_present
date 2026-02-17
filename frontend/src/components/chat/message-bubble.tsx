"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ChartCard } from "@/components/charts/chart-card";
import { cn } from "@/lib/utils";
import { Bot, User, Loader2, Zap } from "lucide-react";
import type { ChatMessage } from "@/lib/types";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const hasCharts = message.charts.length > 0;
  const isChartOnly = hasCharts && !message.content;

  // Chart-only bubble: no avatar, just the chart card aligned with messages
  if (isChartOnly) {
    return (
      <div className="px-4 pl-[52px] py-1">
        {message.charts.map((chart, i) => (
          <ChartCard key={i} chart={chart} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {/* Message row */}
      <div
        className={cn(
          "flex gap-3 px-4 py-3",
          isUser ? "flex-row-reverse" : "flex-row"
        )}
      >
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback
            className={cn(
              "text-xs",
              isUser
                ? "bg-blue-600 text-white"
                : "bg-zinc-800 text-zinc-300"
            )}
          >
            {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
          </AvatarFallback>
        </Avatar>

        <div
          className={cn(
            "max-w-[85%] space-y-2",
            isUser ? "items-end" : "items-start"
          )}
        >
          {/* Text content */}
          {message.content && (
            <div
              className={cn(
                "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                isUser
                  ? "bg-blue-600 text-white"
                  : "bg-zinc-900 text-zinc-100 border border-border/30"
              )}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="prose prose-sm prose-invert max-w-none prose-p:my-1 prose-headings:my-2 prose-pre:my-2">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ children }) => (
                        <div className="my-3 overflow-x-auto rounded-lg border border-zinc-700">
                          <table className="w-full text-sm">{children}</table>
                        </div>
                      ),
                      thead: ({ children }) => (
                        <thead className="bg-zinc-800/80 text-xs uppercase tracking-wider text-zinc-400">
                          {children}
                        </thead>
                      ),
                      th: ({ children }) => (
                        <th className="px-4 py-2.5 text-left font-semibold">{children}</th>
                      ),
                      td: ({ children }) => (
                        <td className="border-t border-zinc-700/50 px-4 py-2 text-zinc-200">{children}</td>
                      ),
                      tr: ({ children }) => (
                        <tr className="transition-colors hover:bg-zinc-800/40">{children}</tr>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}

              {/* removed streaming cursor — loading state shown on send button */}
            </div>
          )}

          {/* Tool status */}
          {message.toolStatus && message.isStreaming && (
            <div className="flex items-center gap-2 px-2 text-xs text-muted-foreground">
              <Loader2 className="h-3 w-3 animate-spin" />
              {message.toolStatus}
            </div>
          )}

          {/* Token usage badge */}
          {!isUser && message.tokenUsage && !message.isStreaming && (
            <div className="flex items-center gap-1.5 px-2 pt-1">
              <div className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-medium tracking-wide",
                message.tokenUsage.model === "mock"
                  ? "bg-amber-950/50 text-amber-400/80 border border-amber-800/30"
                  : "bg-emerald-950/50 text-emerald-400/80 border border-emerald-800/30"
              )}>
                <Zap className="h-2.5 w-2.5" />
                <span className="uppercase">
                  {message.tokenUsage.model === "mock"
                    ? "Mock Mode"
                    : message.tokenUsage.model.replace("claude-", "").replace("-20250514", "")}
                </span>
                <span className="text-zinc-600">•</span>
                <span>
                  {message.tokenUsage.input_tokens.toLocaleString()} in / {message.tokenUsage.output_tokens.toLocaleString()} out
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Inline charts (if message has both text and charts) */}
      {hasCharts && (
        <div className="px-4 pl-[52px] space-y-3">
          {message.charts.map((chart, i) => (
            <ChartCard key={i} chart={chart} />
          ))}
        </div>
      )}
    </div>
  );
}
