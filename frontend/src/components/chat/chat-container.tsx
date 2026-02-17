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
        <div className="space-y-3">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-32" />
        </div>
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
        <header className="flex items-center justify-between border-b border-border/50 px-6 py-3">
          <div>
            <h2 className="text-sm font-semibold">Performance Analysis</h2>
            <p className="text-xs text-muted-foreground">
              {isConnected ? (
                <span className="flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  Connected
                  {uploadedFiles.length > 0 &&
                    ` | ${uploadedFiles.length} file${uploadedFiles.length > 1 ? "s" : ""} loaded`}
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
                  Disconnected
                </span>
              )}
            </p>
          </div>
        </header>

        {/* Welcome / Empty state */}
        {isEmpty ? (
          <div className="min-h-0 flex-1 overflow-y-auto">
            <div className="flex flex-col items-center justify-center gap-8 px-4 py-16 min-h-full">
              <div className="text-center">
                <h1 className="text-2xl font-bold tracking-tight">
                  PresentMon<span className="text-blue-500">AI</span> Analyzer
                </h1>
                <p className="mt-2 text-sm text-muted-foreground max-w-md mx-auto">
                  Upload a PresentMon CSV log and ask questions about your
                  performance data
                </p>
              </div>

              <div className="w-full max-w-md">
                <FileUpload
                  onUpload={uploadFile}
                  isUploading={isUploading}
                  uploadProgress={uploadProgress}
                  uploadError={uploadError}
                />
              </div>
            </div>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}

        {/* Chat input with tips button */}
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
