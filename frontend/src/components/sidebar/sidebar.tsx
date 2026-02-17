"use client";

import { FileText, Plus, Cpu, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import type { FileInfo } from "@/lib/types";

interface SidebarProps {
  files: FileInfo[];
  onNewSession: () => void;
}

export function Sidebar({ files, onNewSession }: SidebarProps) {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex h-full w-64 flex-col border-r border-border/50 bg-zinc-950">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-border/50 px-4 py-4">
        <Cpu className="h-5 w-5 text-blue-500" />
        <h1 className="text-sm font-bold tracking-tight">
          PresentMon<span className="text-blue-500">AI</span>
        </h1>
      </div>

      {/* New session button */}
      <div className="p-3">
        <Button
          variant="outline"
          className="w-full justify-start gap-2 border-border/50 text-xs"
          onClick={onNewSession}
        >
          <Plus className="h-3 w-3" />
          New Analysis
        </Button>
      </div>

      {/* Uploaded files */}
      <div className="flex-1 overflow-auto px-3">
        <p className="mb-2 px-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Uploaded Files
        </p>
        {files.length === 0 ? (
          <p className="px-1 text-xs text-muted-foreground/60">
            No files uploaded yet
          </p>
        ) : (
          <div className="space-y-1">
            {files.map((f) => (
              <div
                key={f.file_id}
                className="flex items-start gap-2 rounded-md px-2 py-1.5 text-xs hover:bg-zinc-900"
              >
                <FileText className="mt-0.5 h-3.5 w-3.5 shrink-0 text-blue-500" />
                <div className="min-w-0">
                  <p className="truncate font-medium">{f.filename}</p>
                  <p className="text-muted-foreground/60">
                    {f.application} | {f.rows.toLocaleString()} frames
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer / Theme toggle */}
      <div className="border-t border-border/50 p-3">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-2 text-xs text-muted-foreground"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? (
            <Sun className="h-3.5 w-3.5" />
          ) : (
            <Moon className="h-3.5 w-3.5" />
          )}
          {theme === "dark" ? "Light Mode" : "Dark Mode"}
        </Button>
      </div>
    </div>
  );
}
