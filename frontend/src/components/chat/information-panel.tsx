"use client";

import { SymptomsPanel } from "@/components/chat/symptoms-panel";
import { ConfidenceCard } from "@/components/chat/confidence-card";
import { SeverityCard } from "@/components/chat/severity-card";
import { AssessmentProgress } from "@/components/chat/assessment-progress";
import { AgentPipeline } from "@/components/chat/agent-pipeline";
import { MedicalDisclaimer } from "@/components/chat/medical-disclaimer";
import { ChatResponse } from "@/schemas/chat.schema";
import { cn } from "@/lib/utils";
import { Bot } from "lucide-react";

interface InformationPanelProps {
  response: ChatResponse | null;
  isLoading: boolean;
  className?: string;
}

export function InformationPanel({ response, isLoading, className }: InformationPanelProps) {
  const hasData = Boolean(response);

  return (
    <div
      className={cn(
        "flex h-full flex-col gap-4 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-border",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Bot className="h-4 w-4 text-primary" />
        Clinical Context
      </div>

      {/* Agent pipeline (shown while loading or always) */}
      {(isLoading || hasData) && (
        <div className="rounded-xl border border-border/50 bg-card/50 p-4 space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            AI Pipeline
          </h3>
          <AgentPipeline
            currentStep={response?.next_step ?? "intake"}
            isLoading={isLoading}
          />
        </div>
      )}

      {/* Progress */}
      <AssessmentProgress response={response} />

      {/* Symptoms */}
      <SymptomsPanel
        symptoms={response?.symptoms ?? []}
        extractedSymptoms={response?.extracted_symptoms ?? {}}
      />

      {/* Confidence */}
      {hasData && Object.keys(response!.confidence_scores ?? {}).length > 0 && (
        <ConfidenceCard confidenceScores={response!.confidence_scores} />
      )}

      {/* Severity */}
      {hasData && (
        <SeverityCard
          escalationDecision={response!.escalation_decision}
          nextStep={response?.next_step}
        />
      )}

      {/* Empty state */}
      {!hasData && !isLoading && (
        <div className="flex flex-1 flex-col items-center justify-center gap-2 text-center text-muted-foreground">
          <Bot className="h-8 w-8 opacity-30" />
          <p className="text-xs">Clinical data will appear here as you describe your symptoms.</p>
        </div>
      )}

      {/* Disclaimer */}
      <MedicalDisclaimer compact className="mt-auto" />
    </div>
  );
}
