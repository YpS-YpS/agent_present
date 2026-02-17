"use client";

import { useState, useEffect, useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useSession() {
  const [sessionId, setSessionId] = useState<string>("");
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Check localStorage for existing session
    const stored = localStorage.getItem("presentmon_session_id");
    if (stored) {
      setSessionId(stored);
      setIsReady(true);
      return;
    }

    // Create a new session
    fetch(`${API_URL}/api/sessions`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        const id = data.session_id;
        localStorage.setItem("presentmon_session_id", id);
        setSessionId(id);
        setIsReady(true);
      })
      .catch(() => {
        // Fallback: generate client-side session ID
        const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
        localStorage.setItem("presentmon_session_id", id);
        setSessionId(id);
        setIsReady(true);
      });
  }, []);

  const resetSession = useCallback(() => {
    fetch(`${API_URL}/api/sessions`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
        const id = data.session_id;
        localStorage.setItem("presentmon_session_id", id);
        setSessionId(id);
      })
      .catch(() => {
        const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
        localStorage.setItem("presentmon_session_id", id);
        setSessionId(id);
      });
  }, []);

  return { sessionId, isReady, resetSession };
}
