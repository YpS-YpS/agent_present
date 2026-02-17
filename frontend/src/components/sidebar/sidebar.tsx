"use client";

import { FileText, Plus, Cpu, Moon, Sun, Sparkles, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { motion, AnimatePresence } from "framer-motion";
import type { FileInfo } from "@/lib/types";

interface SidebarProps {
  files: FileInfo[];
  onNewSession: () => void;
}

export function Sidebar({ files, onNewSession }: SidebarProps) {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex h-full w-72 flex-col bg-gradient-to-b from-zinc-950 via-zinc-950 to-zinc-900/95 border-r border-white/[0.06]">
      {/* Brand header */}
      <div className="px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-lg shadow-blue-500/20">
            <Cpu className="h-5 w-5 text-white" />
            <div className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full border-2 border-zinc-950 bg-emerald-400" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight">
              PresentMon<span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">AI</span>
            </h1>
            <p className="text-[10px] text-zinc-500 font-medium">Performance Analyzer</p>
          </div>
        </div>
      </div>

      {/* New session button */}
      <div className="px-3 pb-2">
        <Button
          variant="outline"
          className="w-full justify-start gap-2.5 border-white/[0.06] bg-white/[0.03] text-xs font-medium text-zinc-300 hover:bg-white/[0.06] hover:text-white transition-all duration-200 h-9 rounded-xl"
          onClick={onNewSession}
        >
          <div className="flex h-5 w-5 items-center justify-center rounded-md bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-blue-400">
            <Plus className="h-3 w-3" />
          </div>
          New Analysis
        </Button>
      </div>

      {/* Uploaded files */}
      <div className="flex-1 overflow-auto px-3 py-3">
        <div className="flex items-center gap-2 px-2 mb-3">
          <div className="h-px flex-1 bg-gradient-to-r from-white/[0.06] to-transparent" />
          <span className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
            Files
          </span>
          <div className="h-px flex-1 bg-gradient-to-l from-white/[0.06] to-transparent" />
        </div>

        <AnimatePresence mode="popLayout">
          {files.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-white/[0.06] px-4 py-6 text-center"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-800/50">
                <FileText className="h-4 w-4 text-zinc-600" />
              </div>
              <p className="text-[11px] text-zinc-600">
                No files uploaded yet
              </p>
            </motion.div>
          ) : (
            <div className="space-y-1">
              {files.map((f, i) => (
                <motion.div
                  key={f.file_id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05, duration: 0.2 }}
                  className="group flex items-center gap-2.5 rounded-xl px-2.5 py-2 transition-all duration-200 hover:bg-white/[0.04] cursor-default"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/15 transition-colors">
                    <FileText className="h-3.5 w-3.5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-medium text-zinc-300 group-hover:text-white transition-colors">
                      {f.game_name || f.application}
                    </p>
                    <p className="text-[10px] text-zinc-600 group-hover:text-zinc-500 transition-colors">
                      {f.rows.toLocaleString()} frames &middot; {f.duration_seconds}s
                    </p>
                  </div>
                  <ChevronRight className="h-3 w-3 text-zinc-700 opacity-0 group-hover:opacity-100 transition-opacity" />
                </motion.div>
              ))}
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer */}
      <div className="border-t border-white/[0.04] p-3 space-y-1">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-2.5 text-xs text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04] rounded-xl h-8 transition-all duration-200"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? (
            <Sun className="h-3.5 w-3.5" />
          ) : (
            <Moon className="h-3.5 w-3.5" />
          )}
          {theme === "dark" ? "Light Mode" : "Dark Mode"}
        </Button>

        <div className="flex items-center gap-1.5 px-3 py-1">
          <Sparkles className="h-2.5 w-2.5 text-zinc-700" />
          <span className="text-[9px] text-zinc-700 font-medium">
            Powered by Claude AI
          </span>
        </div>
      </div>
    </div>
  );
}
