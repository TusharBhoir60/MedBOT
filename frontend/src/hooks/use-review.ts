import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { reviewService } from "@/services/review.service";
import {
  ReviewTaskResponse,
  ReviewTaskOverride,
  ReviewRejectRequest,
  ReviewCommentCreate,
} from "@/schemas/review.schema";

// Keys for React Query cache
export const reviewKeys = {
  all: ["reviews"] as const,
  queue: () => [...reviewKeys.all, "queue"] as const,
  task: (id: string) => [...reviewKeys.all, "task", id] as const,
};

// 1. Fetch entire queue
export function useReviewQueue() {
  return useQuery({
    queryKey: reviewKeys.queue(),
    queryFn: reviewService.getQueue,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// 2. Fetch single task
export function useReviewTask(taskId: string) {
  return useQuery({
    queryKey: reviewKeys.task(taskId),
    queryFn: () => reviewService.getTask(taskId),
    enabled: !!taskId,
    staleTime: 1000 * 60, // 1 minute
  });
}

// 3. Mutations for actions with optimistic updates
export function useReviewActions(taskId: string) {
  const queryClient = useQueryClient();

  // Helper to safely cast updater type
  const updateTaskInCache = (updater: (old: ReviewTaskResponse | undefined) => ReviewTaskResponse | undefined) => {
    queryClient.setQueryData(reviewKeys.task(taskId), updater);
    queryClient.setQueryData(reviewKeys.queue(), (oldQueue: ReviewTaskResponse[] | undefined) => {
      if (!oldQueue) return oldQueue;
      return oldQueue.map((t) => (t.id === taskId ? (updater(t) ?? t) : t));
    });
  };

  const assignTask = useMutation({
    mutationFn: () => reviewService.assignTask(taskId),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: reviewKeys.task(taskId) });
      const prev = queryClient.getQueryData<ReviewTaskResponse>(reviewKeys.task(taskId));
      updateTaskInCache((old) => old ? { ...old, status: "ASSIGNED" } : undefined);
      return { prev };
    },
    onError: (_err, _var, context) => {
      if (context?.prev) updateTaskInCache(() => context.prev);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: reviewKeys.task(taskId) });
      void queryClient.invalidateQueries({ queryKey: reviewKeys.queue() });
    },
  });

  const approveTask = useMutation({
    mutationFn: () => reviewService.approveTask(taskId),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: reviewKeys.task(taskId) });
      const prev = queryClient.getQueryData<ReviewTaskResponse>(reviewKeys.task(taskId));
      updateTaskInCache((old) => old ? { ...old, status: "APPROVED" } : undefined);
      return { prev };
    },
    onError: (_err, _var, context) => {
      if (context?.prev) updateTaskInCache(() => context.prev);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: reviewKeys.task(taskId) });
      void queryClient.invalidateQueries({ queryKey: reviewKeys.queue() });
    },
  });

  const rejectTask = useMutation({
    mutationFn: (data: ReviewRejectRequest) => reviewService.rejectTask(taskId, data),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: reviewKeys.task(taskId) });
      const prev = queryClient.getQueryData<ReviewTaskResponse>(reviewKeys.task(taskId));
      updateTaskInCache((old) => old ? { ...old, status: "REJECTED" } : undefined);
      return { prev };
    },
    onError: (_err, _var, context) => {
      if (context?.prev) updateTaskInCache(() => context.prev);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: reviewKeys.task(taskId) });
      void queryClient.invalidateQueries({ queryKey: reviewKeys.queue() });
    },
  });

  const overrideTask = useMutation({
    mutationFn: (data: ReviewTaskOverride) => reviewService.overrideTask(taskId, data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: reviewKeys.task(taskId) });
      const prev = queryClient.getQueryData<ReviewTaskResponse>(reviewKeys.task(taskId));
      updateTaskInCache((old) => old ? { ...old, status: "OVERRIDDEN", final_response: data.final_response } : undefined);
      return { prev };
    },
    onError: (_err, _var, context) => {
      if (context?.prev) updateTaskInCache(() => context.prev);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: reviewKeys.task(taskId) });
      void queryClient.invalidateQueries({ queryKey: reviewKeys.queue() });
    },
  });

  const addComment = useMutation({
    mutationFn: (data: ReviewCommentCreate) => reviewService.addComment(taskId, data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: reviewKeys.task(taskId) });
      const prev = queryClient.getQueryData<ReviewTaskResponse>(reviewKeys.task(taskId));
      
      const fakeId = `temp-${Date.now()}`;
      updateTaskInCache((old) => {
        if (!old) return old;
        return {
          ...old,
          comments: [...(old.comments ?? []), { id: fakeId, content: data.content, author_id: "You" }]
        };
      });

      return { prev };
    },
    onError: (_err, _var, context) => {
      if (context?.prev) updateTaskInCache(() => context.prev);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: reviewKeys.task(taskId) });
    },
  });

  return {
    assignTask,
    approveTask,
    rejectTask,
    overrideTask,
    addComment,
  };
}
