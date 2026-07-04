"use client";

import { motion, AnimatePresence } from "framer-motion";
import { memo, useMemo } from "react";
import {
  AlertTriangle,
  ChevronRight,
  Stethoscope,
  ListChecks,
  HelpCircle,
  BookOpen,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatResponse } from "@/schemas/chat.schema";

interface AIResponseCardProps {
  response: ChatResponse;
  className?: string;
}

function ConfidencePill({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 80
      ? "bg-emerald-500/20 text-emerald-300 ring-emerald-500/30"
      : pct >= 60
      ? "bg-amber-500/20 text-amber-300 ring-amber-500/30"
      : "bg-red-500/20 text-red-300 ring-red-500/30";
  return (
    <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium ring-1", color)}>
      {pct}% confidence
    </span>
  );
}

function Section({
  icon: Icon,
  title,
  children,
  accent,
}: {
  icon: React.ElementType;
  title: string;
  children: React.ReactNode;
  accent?: string;
}) {
  return (
    <div className="space-y-2">
      <div className={cn("flex items-center gap-2 text-xs font-semibold uppercase tracking-wider", accent ?? "text-muted-foreground")}>
        <Icon className="h-3.5 w-3.5" />
        {title}
      </div>
      {children}
    </div>
  );
}

export const AIResponseCard = memo(function AIResponseCard({ response, className }: AIResponseCardProps) {
  const conditions = response.possible_conditions ?? [];
  const analysis = response.analysis ?? {};
  const confidenceScores = response.confidence_scores ?? {};
  const isEscalated = response.escalation_decision;
  const nextStep = response.next_step;

  // Extract an overall confidence from the combined or highest score
  const overallConf = useMemo(() => {
    const vals = Object.values(confidenceScores).map(Number).filter(Boolean);
    return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  }, [confidenceScores]);

  const followUpQuestions: string[] = useMemo(() => {
    if (analysis.follow_up_questions && Array.isArray(analysis.follow_up_questions)) {
      return analysis.follow_up_questions as string[];
    }
    return [];
  }, [analysis]);

  const summary: string = useMemo(() => {
    if (typeof analysis.summary === "string") return analysis.summary;
    if (typeof analysis.assessment === "string") return analysis.assessment;
    return "";
  }, [analysis]);

  const recommendations: string[] = useMemo(() => {
    if (Array.isArray(analysis.recommendations)) return analysis.recommendations as string[];
    if (Array.isArray(analysis.recommended_actions)) return analysis.recommended_actions as string[];
    return [];
  }, [analysis]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "overflow-hidden rounded-2xl rounded-bl-sm border border-border/50 bg-card/60 shadow-lg backdrop-blur-sm",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 px-5 py-3">
        <div className="flex items-center gap-2">
          <Stethoscope className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold">Clinical Assessment</span>
        </div>
        {overallConf > 0 && <ConfidencePill score={overallConf} />}
      </div>

      <div className="space-y-5 p-5">
        {/* Escalation warning */}
        <AnimatePresence>
          {isEscalated && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-3 rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-300 ring-1 ring-red-500/30"
            >
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>This case has been flagged for physician review due to high urgency signals.</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Summary */}
        {summary && (
          <Section icon={Activity} title="Assessment Summary">
            <p className="text-sm leading-relaxed text-foreground/80">{summary}</p>
          </Section>
        )}

        {/* Conditions */}
        {conditions.length > 0 && (
          <Section icon={Stethoscope} title="Likely Conditions" accent="text-primary/80">
            <ul className="space-y-2">
              {conditions.slice(0, 5).map((cond, i) => {
                const name = typeof cond === "string" ? cond : (cond as Record<string, string>).name ?? String(i + 1);
                const conf = typeof cond === "object" ? Number((cond as Record<string, unknown>).confidence ?? 0) : 0;
                return (
                  <li key={i} className="flex items-center justify-between rounded-lg bg-muted/30 px-3 py-2 text-sm">
                    <span className="font-medium">{name}</span>
                    {conf > 0 && <ConfidencePill score={conf} />}
                  </li>
                );
              })}
            </ul>
          </Section>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <Section icon={ListChecks} title="Recommended Actions" accent="text-emerald-400/80">
            <ul className="space-y-1.5">
              {recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <ChevronRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-400" />
                  <span className="text-foreground/80">{rec}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Follow-up Questions */}
        {followUpQuestions.length > 0 && (
          <Section icon={HelpCircle} title="Follow-up Questions" accent="text-amber-400/80">
            <ul className="space-y-1.5">
              {followUpQuestions.map((q, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="mt-0.5 text-amber-400">•</span>
                  <span className="italic text-foreground/80">{q}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}

        {/* Next step */}
        {nextStep && (
          <div className="flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/5 px-3 py-2">
            <BookOpen className="h-3.5 w-3.5 shrink-0 text-primary" />
            <span className="text-xs text-muted-foreground">
              Next: <span className="font-medium text-foreground">{nextStep}</span>
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
});
