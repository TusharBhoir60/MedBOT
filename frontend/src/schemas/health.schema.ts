import { z } from "zod";

export const ComponentHealthSchema = z.object({
  status: z.enum(["healthy", "unhealthy", "degraded", "unknown"]),
  latency_ms: z.number().optional(),
  details: z.string().optional(),
});

export const HealthResponseSchema = z.object({
  status: z.enum(["healthy", "unhealthy", "degraded"]),
  version: z.string(),
  environment: z.string(),
  timestamp: z.string(),
  components: z.record(z.string(), ComponentHealthSchema).optional(),
});

export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type ComponentHealth = z.infer<typeof ComponentHealthSchema>;
