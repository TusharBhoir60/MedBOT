import { z } from "zod";

export const ReviewStatusEnum = z.enum([
  "NEW", "ASSIGNED", "UNDER_REVIEW", "APPROVED", "REJECTED", "OVERRIDDEN", "CLOSED"
]);

export const ReviewCommentSchema = z.object({
  id: z.string(),
  author_id: z.string().nullable().optional(),
  content: z.string(),
});

export const ReviewTaskResponseSchema = z.object({
  id: z.string(),
  session_id: z.string(),
  status: ReviewStatusEnum,
  assignee_id: z.string().nullable().optional(),
  patient_info: z.record(z.string(), z.any()),
  symptoms: z.array(z.string()),
  diagnosis_output: z.record(z.string(), z.any()).nullable().optional(),
  final_response: z.record(z.string(), z.any()).nullable().optional(),
  comments: z.array(ReviewCommentSchema).default([]),
});

export const ReviewTaskOverrideSchema = z.object({
  final_response: z.record(z.string(), z.any()),
});

export const ReviewRejectRequestSchema = z.object({
  reason: z.string().optional(),
});

export const ReviewCommentCreateSchema = z.object({
  content: z.string(),
});

export type ReviewStatus = z.infer<typeof ReviewStatusEnum>;
export type ReviewTaskResponse = z.infer<typeof ReviewTaskResponseSchema>;
export type ReviewTaskOverride = z.infer<typeof ReviewTaskOverrideSchema>;
export type ReviewRejectRequest = z.infer<typeof ReviewRejectRequestSchema>;
export type ReviewCommentCreate = z.infer<typeof ReviewCommentCreateSchema>;
export type ReviewComment = z.infer<typeof ReviewCommentSchema>;
