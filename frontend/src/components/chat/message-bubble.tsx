"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ChartCard } from "@/components/charts/chart-card";
import { cn } from "@/lib/utils";
import { Bot, User, Loader2, Zap, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
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
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="px-4 pl-[56px] py-1"
      >
        {message.charts.map((chart, i) => (
          <ChartCard key={i} chart={chart} />
        ))}
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-2"
    >
      {/* Message row */}
      <div
        className={cn(
          "flex gap-3 px-4 py-3",
          isUser ? "flex-row-reverse" : "flex-row"
        )}
      >
        {/* Avatar */}
        <Avatar className="h-8 w-8 shrink-0 shadow-md">
          <AvatarFallback
            className={cn(
              "text-xs",
              isUser
                ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white"
                : "bg-gradient-to-br from-zinc-800 to-zinc-900 text-zinc-300 border border-white/[0.06]"
            )}
          >
            {isUser ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
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
                "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                isUser
                  ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/10"
                  : "bg-zinc-900/80 text-zinc-100 border border-white/[0.06] backdrop-blur-sm"
              )}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="prose prose-sm prose-invert max-w-none prose-p:my-1.5 prose-headings:my-2.5 prose-pre:my-2 prose-headings:text-zinc-100">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ children }) => (
                        <div className="my-3 overflow-x-auto rounded-xl border border-white/[0.06] bg-zinc-950/50">
                          <table className="w-full text-sm">{children}</table>
                        </div>
                      ),
                      thead: ({ children }) => (
                        <thead className="bg-white/[0.03] text-[10px] uppercase tracking-wider text-zinc-400">
                          {children}
                        </thead>
                      ),
                      th: ({ children }) => (
                        <th className="px-4 py-2.5 text-left font-semibold">{children}</th>
                      ),
                      td: ({ children }) => (
                        <td className="border-t border-white/[0.04] px-4 py-2 text-zinc-200">{children}</td>
                      ),
                      tr: ({ children }) => (
                        <tr className="transition-colors hover:bg-white/[0.02]">{children}</tr>
                      ),
                      code: ({ children, className }) => {
                        const isInline = !className;
                        return isInline ? (
                          <code className="rounded-md bg-white/[0.06] px-1.5 py-0.5 text-[12px] font-mono text-cyan-300">
                            {children}
                          </code>
                        ) : (
                          <code className={className}>{children}</code>
                        );
                      },
                      strong: ({ children }) => (
                        <strong className="font-semibold text-white">{children}</strong>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          )}

          {/* Tool status */}
          {message.toolStatus && message.isStreaming && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-2 px-2 text-xs text-zinc-500"
            >
              <Loader2 className="h-3 w-3 animate-spin text-blue-400" />
              <span className="font-medium">{message.toolStatus}</span>
            </motion.div>
          )}

          {/* Token usage badge */}
          {!isUser && message.tokenUsage && !message.isStreaming && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center gap-1.5 px-2 pt-1"
            >
              <div className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-medium tracking-wide",
                message.tokenUsage.model === "mock"
                  ? "bg-amber-500/8 text-amber-400/80 border border-amber-500/10"
                  : "bg-emerald-500/8 text-emerald-400/80 border border-emerald-500/10"
              )}>
                <Zap className="h-2.5 w-2.5" />
                <span className="uppercase">
                  {message.tokenUsage.model === "mock"
                    ? "Mock"
                    : message.tokenUsage.model.replace("claude-", "").replace("-20250514", "")}
                </span>
                <span className="text-zinc-700">&middot;</span>
                <span>
                  {message.tokenUsage.input_tokens.toLocaleString()} in / {message.tokenUsage.output_tokens.toLocaleString()} out
                </span>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Inline charts (if message has both text and charts) */}
      {hasCharts && (
        <div className="px-4 pl-[56px] space-y-3">
          {message.charts.map((chart, i) => (
            <ChartCard key={i} chart={chart} />
          ))}
        </div>
      )}
    </motion.div>
  );
}
