"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
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
          "relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors",
          isDragOver
            ? "border-blue-500 bg-blue-500/10"
            : "border-border/50 hover:border-border"
        )}
      >
        <Upload className="mb-2 h-8 w-8 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          Drag & drop a CSV file, or{" "}
          <label className="cursor-pointer text-blue-500 hover:underline">
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
        <p className="mt-1 text-xs text-muted-foreground/60">
          PresentMon CSV logs supported
        </p>

        {isUploading && (
          <div className="mt-3 w-full max-w-xs">
            <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div
                className="h-full rounded-full bg-blue-500 transition-all"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="mt-1 text-center text-xs text-muted-foreground">
              Uploading... {uploadProgress}%
            </p>
          </div>
        )}
      </div>

      {uploadError && (
        <div className="flex items-center gap-2 rounded-md bg-red-500/10 px-3 py-2 text-sm text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {uploadError}
        </div>
      )}

      {lastUpload && !isUploading && (
        <div className="flex items-center gap-2 rounded-md bg-green-500/10 px-3 py-2 text-sm text-green-400">
          <CheckCircle className="h-4 w-4 shrink-0" />
          <div>
            <span className="font-medium">{lastUpload.filename}</span>
            {" — "}
            {lastUpload.application} | {lastUpload.rows.toLocaleString()} frames |{" "}
            {lastUpload.duration_seconds}s | ~
            {lastUpload.profile.avg_fps?.toFixed(0) || "?"} FPS avg
          </div>
        </div>
      )}
    </div>
  );
}
