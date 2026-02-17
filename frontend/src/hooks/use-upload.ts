"use client";

import { useState, useCallback } from "react";
import type { FileInfo } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useUpload(sessionId: string) {
  const [uploadedFiles, setUploadedFiles] = useState<FileInfo[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const uploadFile = useCallback(
    async (file: File) => {
      if (!sessionId) return null;

      setIsUploading(true);
      setUploadProgress(0);
      setUploadError(null);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const xhr = new XMLHttpRequest();

        const result = await new Promise<FileInfo>((resolve, reject) => {
          xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
              setUploadProgress(Math.round((e.loaded / e.total) * 100));
            }
          });

          xhr.addEventListener("load", () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(JSON.parse(xhr.responseText));
            } else {
              try {
                const err = JSON.parse(xhr.responseText);
                reject(new Error(err.detail || `Upload failed (${xhr.status})`));
              } catch {
                reject(new Error(`Upload failed (${xhr.status})`));
              }
            }
          });

          xhr.addEventListener("error", () => reject(new Error("Network error")));
          xhr.open("POST", `${API_URL}/api/upload/${sessionId}`);
          xhr.send(formData);
        });

        setUploadedFiles((prev) => [...prev, result]);
        return result;
      } catch (e: any) {
        setUploadError(e.message || "Upload failed");
        return null;
      } finally {
        setIsUploading(false);
        setUploadProgress(0);
      }
    },
    [sessionId]
  );

  return { uploadedFiles, uploadFile, isUploading, uploadProgress, uploadError };
}
