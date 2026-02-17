"use client";

import { useState } from "react";
import { useSession } from "@/hooks/use-session";
import { useChat } from "@/hooks/use-chat";
import { useUpload } from "@/hooks/use-upload";
import { Sidebar } from "@/components/sidebar/sidebar";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import { FileUpload } from "@/components/upload/file-upload";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";
import { Cpu, Wifi, WifiOff, BarChart3, Zap, Activity } from "lucide-react";

export function ChatContainer() {
  const { sessionId, isReady, resetSession } = useSession();
  const { messages, sendMessage, isConnected, isLoading, clearMessages } =
    useChat(sessionId);
  const { uploadedFiles, uploadFile, isUploading, uploadProgress, uploadError } =
    useUpload(sessionId);

  const handleNewSession = () => {
    resetSession();
    clearMessages();
  };

  if (!isReady) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-3"
        >
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-32" />
        </motion.div>
      </div>
    );
  }

  const isEmpty = messages.length === 0;

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar files={uploadedFiles} onNewSession={handleNewSession} />

      {/* Main Area */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Header bar */}
        <header className="flex items-center justify-between border-b border-white/[0.06] bg-zinc-950/50 backdrop-blur-sm px-6 py-2.5">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-zinc-200">
              {uploadedFiles.length > 0
                ? uploadedFiles[uploadedFiles.length - 1].game_name || uploadedFiles[uploadedFiles.length - 1].application
                : "Performance Analysis"}
            </h2>
            <div className="h-4 w-px bg-white/[0.06]" />
            <div className="flex items-center gap-1.5">
              {isConnected ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-[10px] font-medium text-emerald-400"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse-glow" />
                  Live
                </motion.div>
              ) : (
                <div className="flex items-center gap-1.5 rounded-full bg-red-500/10 px-2.5 py-1 text-[10px] font-medium text-red-400">
                  <WifiOff className="h-2.5 w-2.5" />
                  Offline
                </div>
              )}
              {uploadedFiles.length > 0 && (
                <div className="flex items-center gap-1 rounded-full bg-blue-500/10 px-2.5 py-1 text-[10px] font-medium text-blue-400">
                  <BarChart3 className="h-2.5 w-2.5" />
                  {uploadedFiles.length} file{uploadedFiles.length > 1 ? "s" : ""}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Welcome / Empty state */}
        {isEmpty ? (
          <div className="min-h-0 flex-1 overflow-y-auto">
            <div className="flex flex-col items-center justify-center gap-10 px-4 py-16 min-h-full">
              {/* Hero */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-center"
              >
                <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-xl shadow-blue-500/25">
                  <Cpu className="h-8 w-8 text-white" />
                </div>
                <h1 className="text-3xl font-bold tracking-tight">
                  PresentMon<span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">AI</span>
                </h1>
                <p className="mt-3 text-sm text-zinc-500 max-w-md mx-auto leading-relaxed">
                  Upload a PresentMon CSV log and get AI-powered insights into
                  your GPU & CPU performance
                </p>
              </motion.div>

              {/* Upload zone */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.15 }}
                className="w-full max-w-lg"
              >
                <FileUpload
                  onUpload={uploadFile}
                  isUploading={isUploading}
                  uploadProgress={uploadProgress}
                  uploadError={uploadError}
                />
              </motion.div>

              {/* Feature pills */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="flex flex-wrap justify-center gap-2"
              >
                {[
                  { icon: Zap, label: "FPS Analysis" },
                  { icon: Activity, label: "Stutter Detection" },
                  { icon: BarChart3, label: "Interactive Charts" },
                  { icon: Cpu, label: "CPU/GPU Bottleneck" },
                ].map((feat) => (
                  <div
                    key={feat.label}
                    className="flex items-center gap-1.5 rounded-full border border-white/[0.06] bg-white/[0.02] px-3 py-1.5 text-[11px] text-zinc-500"
                  >
                    <feat.icon className="h-3 w-3 text-zinc-600" />
                    {feat.label}
                  </div>
                ))}
              </motion.div>
            </div>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}

        {/* Chat input */}
        <ChatInput
          onSend={sendMessage}
          onFileUpload={uploadFile}
          isLoading={isLoading}
          isConnected={isConnected}
        />
      </div>
    </div>
  );
}
