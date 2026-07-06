import { z } from "zod";

export const ChatRequestSchema = z.object({
  session_id: z.string().uuid(),
  message: z.string(),
  patient_info: z.record(z.string(), z.any()).optional(),
  symptoms: z.array(z.string()).optional(),
});

export const MessageSchema = z.object({
  role: z.enum(["human", "ai", "system"]),
  content: z.string(),
});

export const ChatResponseSchema = z.object({
  session_id: z.string(),
  turn_count: z.number(),
  messages: z.array(MessageSchema),
  patient_info: z.record(z.string(), z.any()),
  symptoms: z.array(z.string()),
  extracted_symptoms: z.record(z.string(), z.any()),
  possible_conditions: z.array(z.record(z.string(), z.any())),
  analysis: z.record(z.string(), z.any()),
  confidence_scores: z.record(z.string(), z.number()),
  escalation_decision: z.boolean(),
  next_step: z.string(),
});

export type ChatRequest = z.infer<typeof ChatRequestSchema>;
export type ChatResponse = z.infer<typeof ChatResponseSchema>;
export type ChatMessage = z.infer<typeof MessageSchema>;
