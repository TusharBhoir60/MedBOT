"use client";

import { memo } from "react";
import { CheckCircle2, Circle } from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatResponse } from "@/schemas/chat.schema";

interface AssessmentProgressProps {
  response: ChatResponse | null;
  className?: string;
}

const PHASES = [
  { id: "info", label: "Patient Information", key: "patient_info" },
  { id: "symptoms", label: "Symptoms Collected", key: "symptoms" },
  { id: "analysis", label: "Analysis Complete", key: "analysis" },
  { id: "diagnosis", label: "Differential Diagnosis", key: "possible_conditions" },
  { id: "followup", label: "Follow-up", key: "next_step" },
];

function isPhaseComplete(phase: typeof PHASES[0], response: ChatResponse | null): boolean {
  if (!response) return false;
  const val = response[phase.key as keyof ChatResponse];
  if (Array.isArray(val)) return val.length > 0;
  if (typeof val === "object" && val !== null) return Object.keys(val).length > 0;
  if (typeof val === "string") return val.length > 0 && val !== "intake";
  return Boolean(val);
}

export const AssessmentProgress = memo(function AssessmentProgress({ response, className }: AssessmentProgressProps) {
  const completedCount = PHASES.filter((p) => isPhaseComplete(p, response)).length;
  const pct = Math.round((completedCount / PHASES.length) * 100);

  return (
    <div className={cn("rounded-xl border border-border/50 bg-card/50 p-4 space-y-4", className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Assessment Progress
        </h3>
        <span className="text-xs font-medium text-primary">{pct}%</span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 overflow-hidden rounded-full bg-muted/30">
        <div
          className="h-full rounded-full bg-primary transition-all duration-700 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Steps */}
      <ul className="space-y-2.5">
        {PHASES.map((phase) => {
          const done = isPhaseComplete(phase, response);
          return (
            <li key={phase.id} className="flex items-center gap-2.5">
              {done ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
              ) : (
                <Circle className="h-4 w-4 shrink-0 text-muted-foreground/30" />
              )}
              <span className={cn("text-xs", done ? "text-foreground" : "text-muted-foreground/50")}>
                {phase.label}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
});
