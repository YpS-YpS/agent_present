"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Send,
  Square,
  Paperclip,
  Loader2,
  Lightbulb,
  X,
  Zap,
  Cpu,
  Activity,
  Thermometer,
  LineChart,
  Info,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import type { FileInfo } from "@/lib/types";

/* ------------------------------------------------------------------ */
/*  Prompt tips data                                                   */
/* ------------------------------------------------------------------ */

interface TipCategory {
  label: string;
  color: string;
  icon: LucideIcon;
  queries: string[];
}

const TIP_CATEGORIES: TipCategory[] = [
  {
    label: "FPS & Frame Time",
    color: "text-blue-400",
    icon: Zap,
    queries: [
      "What's my average FPS?",
      "Show 1% and 0.1% low FPS",
      "Show me a frame time chart",
      "Plot FPS distribution histogram",
    ],
  },
  {
    label: "CPU / GPU Bottleneck",
    color: "text-emerald-400",
    icon: Cpu,
    queries: [
      "Is this game CPU or GPU bound?",
      "Show CPU busy vs GPU busy stats",
      "Plot CPU busy vs GPU busy over time",
      "What's the frame overhead?",
    ],
  },
  {
    label: "Stutters & Latency",
    color: "text-amber-400",
    icon: Activity,
    queries: [
      "Are there any stutters?",
      "Show worst frame time spikes",
      "What's the display latency?",
      "Analyze input-to-photon latency",
    ],
  },
  {
    label: "GPU Power & Thermals",
    color: "text-red-400",
    icon: Thermometer,
    queries: [
      "Is there any GPU throttling?",
      "Plot GPU power and temperature",
      "Show GPU & CPU utilization over time",
      "Is the GPU power limited?",
    ],
  },
  {
    label: "Charts & Visualization",
    color: "text-violet-400",
    icon: LineChart,
    queries: [
      "Visualize the performance",
      "Draw a frame time timeline",
      "Show a bottleneck chart",
      "Plot CPU & GPU utilization",
    ],
  },
  {
    label: "Data & Comparison",
    color: "text-cyan-400",
    icon: Info,
    queries: [
      "What data is in this file?",
      "Give me a full performance summary",
      "Show per-10-second segment stats",
      "Compare uploaded files",
    ],
  },
];

/* ------------------------------------------------------------------ */

interface ChatInputProps {
  onSend: (message: string) => void;
  onFileUpload: (file: File) => Promise<FileInfo | null>;
  isLoading: boolean;
  isConnected: boolean;
}

export function ChatInput({
  onSend,
  onFileUpload,
  isLoading,
  isConnected,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const [tipsOpen, setTipsOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const tipsRef = useRef<HTMLDivElement>(null);

  // Close tips when clicking outside
  useEffect(() => {
    if (!tipsOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (tipsRef.current && !tipsRef.current.contains(e.target as Node)) {
        setTipsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [tipsOpen]);

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [input, isLoading, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await onFileUpload(file);
    }
    e.target.value = "";
  };

  const handleTipClick = (query: string) => {
    setTipsOpen(false);
    onSend(query);
  };

  return (
    <div className="relative border-t border-white/[0.06] bg-zinc-950/80 backdrop-blur-sm px-4 py-3">
      {/* Tips popup */}
      <AnimatePresence>
        {tipsOpen && (
          <motion.div
            ref={tipsRef}
            initial={{ opacity: 0, y: 10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-full left-0 right-0 z-50 mb-2 px-4"
          >
            <div className="mx-auto max-w-3xl rounded-2xl border border-white/[0.06] bg-zinc-950/95 backdrop-blur-xl shadow-2xl shadow-black/50">
              {/* Popup header */}
              <div className="flex items-center justify-between border-b border-white/[0.04] px-5 py-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-amber-500/10">
                    <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
                  </div>
                  <span className="text-sm font-semibold text-zinc-200">Prompt Tips</span>
                </div>
                <button
                  onClick={() => setTipsOpen(false)}
                  className="rounded-lg p-1.5 text-zinc-500 transition-colors hover:bg-white/[0.04] hover:text-zinc-300"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Tip categories grid */}
              <div className="max-h-[60vh] overflow-y-auto p-4">
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                  {TIP_CATEGORIES.map((cat) => (
                    <div key={cat.label} className="space-y-2">
                      <div className="flex items-center gap-1.5">
                        <cat.icon className={`h-3.5 w-3.5 ${cat.color}`} />
                        <span
                          className={`text-[10px] font-semibold uppercase tracking-wider ${cat.color}`}
                        >
                          {cat.label}
                        </span>
                      </div>
                      <div className="space-y-1">
                        {cat.queries.map((q) => (
                          <button
                            key={q}
                            onClick={() => handleTipClick(q)}
                            className="w-full text-left rounded-lg bg-white/[0.02] border border-white/[0.04] px-2.5 py-1.5 text-[11px] text-zinc-400 transition-all hover:bg-white/[0.06] hover:text-white hover:border-white/[0.08]"
                          >
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input bar */}
      <div className="mx-auto flex max-w-3xl items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 shrink-0 rounded-xl text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04] transition-all duration-200"
          onClick={handleFileClick}
          title="Upload CSV file"
        >
          <Paperclip className="h-4 w-4" />
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
        />

        {/* Tips button */}
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            "h-10 w-10 shrink-0 rounded-xl transition-all duration-200",
            tipsOpen
              ? "text-amber-400 bg-amber-500/10"
              : "text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04]"
          )}
          onClick={() => setTipsOpen(!tipsOpen)}
          title="Prompt tips"
        >
          <Lightbulb className="h-4 w-4" />
        </Button>

        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder={
              isConnected
                ? "Ask about your performance data..."
                : "Connecting..."
            }
            disabled={!isConnected}
            rows={1}
            className={cn(
              "w-full resize-none rounded-xl border border-white/[0.06] bg-white/[0.03] px-4 py-2.5 text-sm text-foreground placeholder:text-zinc-600 focus:border-blue-500/30 focus:outline-none focus:ring-1 focus:ring-blue-500/20 focus:bg-white/[0.04] transition-all duration-200",
              !isConnected && "opacity-50"
            )}
          />
        </div>

        <Button
          size="icon"
          className={cn(
            "h-10 w-10 shrink-0 rounded-xl transition-all duration-300 shadow-lg",
            isLoading
              ? "bg-gradient-to-br from-red-500 to-red-600 hover:from-red-400 hover:to-red-500 shadow-red-500/25 animate-pulse"
              : input.trim()
                ? "bg-gradient-to-br from-emerald-500 to-green-500 hover:from-emerald-400 hover:to-green-400 shadow-emerald-500/25 scale-100 hover:scale-105"
                : "bg-zinc-800 hover:bg-zinc-700 shadow-none"
          )}
          onClick={handleSubmit}
          disabled={(!input.trim() && !isLoading) || !isConnected}
        >
          {isLoading ? (
            <Square className="h-3.5 w-3.5 fill-current" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  );
}
