"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, CheckCircle, AlertCircle, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import type { FileInfo } from "@/lib/types";

interface FileUploadProps {
  onUpload: (file: File) => Promise<FileInfo | null>;
  isUploading: boolean;
  uploadProgress: number;
  uploadError: string | null;
}

export function FileUpload({
  onUpload,
  isUploading,
  uploadProgress,
  uploadError,
}: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [lastUpload, setLastUpload] = useState<FileInfo | null>(null);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        const result = await onUpload(file);
        if (result) setLastUpload(result);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        const result = await onUpload(file);
        if (result) setLastUpload(result);
      }
      e.target.value = "";
    },
    [onUpload]
  );

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={cn(
          "relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 transition-all duration-300",
          isDragOver
            ? "border-blue-400/50 bg-blue-500/5 scale-[1.01] shadow-lg shadow-blue-500/5"
            : "border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.02]"
        )}
      >
        <motion.div
          animate={isDragOver ? { scale: 1.1, y: -4 } : { scale: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className={cn(
            "mb-3 flex h-12 w-12 items-center justify-center rounded-2xl transition-colors duration-300",
            isDragOver
              ? "bg-blue-500/15 text-blue-400"
              : "bg-white/[0.04] text-zinc-500"
          )}
        >
          <Upload className="h-6 w-6" />
        </motion.div>

        <p className="text-sm text-zinc-400">
          Drag & drop a CSV file, or{" "}
          <label className="cursor-pointer font-medium text-blue-400 hover:text-blue-300 transition-colors">
            browse
            <input
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleFileSelect}
              disabled={isUploading}
            />
          </label>
        </p>
        <p className="mt-1.5 text-xs text-zinc-600">
          PresentMon CSV logs supported
        </p>

        <AnimatePresence>
          {isUploading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-4 w-full max-w-xs"
            >
              <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800/50">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              <p className="mt-1.5 text-center text-xs text-zinc-500">
                Uploading... {uploadProgress}%
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {uploadError && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 rounded-xl bg-red-500/8 border border-red-500/10 px-3.5 py-2.5 text-sm text-red-400"
          >
            <AlertCircle className="h-4 w-4 shrink-0" />
            {uploadError}
          </motion.div>
        )}

        {lastUpload && !isUploading && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2.5 rounded-xl bg-emerald-500/8 border border-emerald-500/10 px-3.5 py-2.5 text-sm text-emerald-400"
          >
            <CheckCircle className="h-4 w-4 shrink-0" />
            <div>
              <span className="font-medium">{lastUpload.game_name || lastUpload.application}</span>
              {" — "}
              {lastUpload.rows.toLocaleString()} frames |{" "}
              {lastUpload.duration_seconds}s | ~
              {lastUpload.profile.avg_fps?.toFixed(0) || "?"} FPS avg
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
