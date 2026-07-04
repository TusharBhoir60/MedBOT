"use client";

import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface AgentStatusProps {
  agent: "intake" | "symptom" | "diagnosis" | "followup" | "idle";
  className?: string;
}

const AGENT_LABELS: Record<string, string> = {
  intake: "Gathering Patient Info",
  symptom: "Analyzing Symptoms",
  diagnosis: "Running Differential Diagnosis",
  followup: "Generating Follow-up",
  idle: "Ready",
};

export function AgentStatus({ agent, className }: AgentStatusProps) {
  const isActive = agent !== "idle";

  return (
    <div
      className={cn(
        "flex items-center gap-2 text-xs text-muted-foreground",
        className
      )}
    >
      {isActive ? (
        <>
          <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
          <span className="animate-pulse">{AGENT_LABELS[agent]}</span>
        </>
      ) : (
        <>
          <span className="h-2 w-2 rounded-full bg-success" />
          <span>{AGENT_LABELS.idle}</span>
        </>
      )}
    </div>
  );
}
