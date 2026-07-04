"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: "intake", label: "Patient Intake", description: "Collecting your information" },
  { id: "symptoms", label: "Symptom Analysis", description: "Analyzing reported symptoms" },
  { id: "diagnosis", label: "Differential Diagnosis", description: "Evaluating possible conditions" },
  { id: "followup", label: "Follow-up Questions", description: "Refining the assessment" },
];

type StepStatus = "done" | "active" | "pending";

interface AgentPipelineProps {
  currentStep?: string;
  isLoading?: boolean;
  className?: string;
}

function getStepStatus(stepId: string, currentStep: string, isLoading: boolean): StepStatus {
  const currentIdx = STEPS.findIndex((s) => s.id === currentStep);
  const stepIdx = STEPS.findIndex((s) => s.id === stepId);
  if (stepIdx < currentIdx) return "done";
  if (stepIdx === currentIdx) return isLoading ? "active" : "done";
  return "pending";
}

export function AgentPipeline({ currentStep = "intake", isLoading = false, className }: AgentPipelineProps) {
  return (
    <div className={cn("space-y-2", className)}>
      {STEPS.map((step) => {
        const status = getStepStatus(step.id, currentStep, isLoading);
        return (
          <div key={step.id} className="flex items-start gap-3">
            {/* Icon */}
            <div className="mt-0.5 shrink-0">
              {status === "done" && (
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              )}
              {status === "active" && (
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
              )}
              {status === "pending" && (
                <Circle className="h-4 w-4 text-muted-foreground/30" />
              )}
            </div>

            {/* Label */}
            <div className="min-w-0">
              <p className={cn(
                "text-xs font-medium leading-none",
                status === "done" && "text-emerald-400",
                status === "active" && "text-primary",
                status === "pending" && "text-muted-foreground/50"
              )}>
                {step.label}
              </p>
              {status === "active" && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-0.5 text-xs text-muted-foreground"
                >
                  {step.description}
                </motion.p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
