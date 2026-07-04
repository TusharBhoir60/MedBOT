import { apiClient } from "@/lib/api-client";
import { ChatRequest, ChatResponse } from "@/schemas/chat.schema";

export const chatService = {
  invoke: async (data: ChatRequest): Promise<ChatResponse> => {
    return apiClient.post<ChatResponse>("/api/v1/chat/invoke", data);
  },
};
