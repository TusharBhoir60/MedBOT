"use client";

import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { chatService, ConversationSummary } from "@/services/chat.service";
import { ChatResponse } from "@/schemas/chat.schema";

export type LocalMessage = {
  id: string;
  role: "human" | "ai";
  content: string;
  timestamp: Date;
};

export type ChatState = {
  sessionId: string;
  messages: LocalMessage[];
  isLoading: boolean;
  latestResponse: ChatResponse | null;
  error: string | null;
};

export function useChat() {
  const [sessionId, setSessionId] = useState<string>(() => uuidv4());
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [latestResponse, setLatestResponse] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      setError(null);

      // Optimistic user message
      const userMsg: LocalMessage = {
        id: uuidv4(),
        role: "human",
        content: content.trim(),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      try {
        const response = await chatService.invoke({
          session_id: sessionId,
          message: content.trim(),
          patient_info: {},
          symptoms: [],
        });

        setLatestResponse(response);

        // Extract AI messages from response
        const aiMessages = response.messages
          .filter((m) => m.role === "ai")
          .slice(-1); // last AI turn

        if (aiMessages.length > 0) {
          const aiMsg: LocalMessage = {
            id: uuidv4(),
            role: "ai",
            content: aiMessages[0].content,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, aiMsg]);
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "An error occurred. Please try again.";
        setError(message);
        // Remove optimistic message on failure
        setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, isLoading]
  );

  const startNewChat = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    setSessionId(uuidv4());
    setMessages([]);
    setLatestResponse(null);
    setError(null);
    setIsLoading(false);
  }, []);

  const loadSession = useCallback(async (summary: ConversationSummary) => {
    try {
      const detail = await chatService.getSession(summary.session_id);
      setSessionId(summary.session_id);
      setLatestResponse(detail.state);

      // Reconstruct local messages from stored state
      const msgs: LocalMessage[] = (detail.state.messages ?? [])
        .filter((m) => m.role === "human" || m.role === "ai")
        .map((m) => ({
          id: uuidv4(),
          role: m.role as "human" | "ai",
          content: m.content,
          timestamp: new Date(summary.updated_at),
        }));

      setMessages(msgs);
      setError(null);
    } catch {
      setError("Failed to load conversation.");
    }
  }, []);

  return {
    sessionId,
    messages,
    isLoading,
    latestResponse,
    error,
    sendMessage,
    startNewChat,
    loadSession,
  };
}
