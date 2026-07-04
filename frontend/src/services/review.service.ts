import { apiClient } from "@/lib/api-client";
import {
  ReviewTaskResponse,
  ReviewTaskOverride,
  ReviewRejectRequest,
  ReviewCommentCreate,
} from "@/schemas/review.schema";

export const reviewService = {
  getQueue: async (): Promise<ReviewTaskResponse[]> => {
    return apiClient.get<ReviewTaskResponse[]>("/api/v1/review/queue");
  },

  getTask: async (taskId: string): Promise<ReviewTaskResponse> => {
    return apiClient.get<ReviewTaskResponse>(`/api/v1/review/${taskId}`);
  },

  assignTask: async (taskId: string): Promise<ReviewTaskResponse> => {
    return apiClient.post<ReviewTaskResponse>(`/api/v1/review/${taskId}/assign`);
  },

  approveTask: async (taskId: string): Promise<ReviewTaskResponse> => {
    return apiClient.post<ReviewTaskResponse>(`/api/v1/review/${taskId}/approve`);
  },

  overrideTask: async (taskId: string, data: ReviewTaskOverride): Promise<ReviewTaskResponse> => {
    return apiClient.post<ReviewTaskResponse>(`/api/v1/review/${taskId}/override`, data);
  },

  rejectTask: async (taskId: string, data: ReviewRejectRequest): Promise<ReviewTaskResponse> => {
    return apiClient.post<ReviewTaskResponse>(`/api/v1/review/${taskId}/reject`, data);
  },

  addComment: async (taskId: string, data: ReviewCommentCreate): Promise<ReviewTaskResponse> => {
    return apiClient.post<ReviewTaskResponse>(`/api/v1/review/${taskId}/comments`, data);
  },
};
