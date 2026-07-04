import { apiClient } from "@/lib/api-client";
import { ChatRequest, ChatResponse } from "@/schemas/chat.schema";

// ── History schemas ──────────────────────────────────────────────────────────

export interface ConversationSummary {
  session_id: string;
  title: string | null;
  is_archived: boolean;
  updated_at: string;
  created_at: string;
  last_message_preview: string | null;
  message_count: number;
}

export interface ConversationDetail {
  session_id: string;
  title: string | null;
  is_archived: boolean;
  updated_at: string;
  created_at: string;
  state: ChatResponse;
}

// ── Service ──────────────────────────────────────────────────────────────────

export const chatService = {
  // Invoke the AI workflow
  invoke: async (data: ChatRequest): Promise<ChatResponse> => {
    return apiClient.post<ChatResponse>("/api/v1/chat/invoke", data);
  },

  // Get all conversation summaries for the current user
  getHistory: async (): Promise<ConversationSummary[]> => {
    return apiClient.get<ConversationSummary[]>("/api/v1/chat/history");
  },

  // Get full detail for a conversation
  getSession: async (sessionId: string): Promise<ConversationDetail> => {
    return apiClient.get<ConversationDetail>(`/api/v1/chat/history/${sessionId}`);
  },

  // Rename a conversation
  renameSession: async (sessionId: string, title: string): Promise<void> => {
    return apiClient.patch(`/api/v1/chat/history/${sessionId}`, { title });
  },

  // Delete a conversation
  deleteSession: async (sessionId: string): Promise<void> => {
    return apiClient.delete(`/api/v1/chat/history/${sessionId}`);
  },

  // Archive a conversation
  archiveSession: async (sessionId: string): Promise<void> => {
    return apiClient.post(`/api/v1/chat/history/${sessionId}/archive`, {});
  },
};
