"use client";

import { memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { ChatResponse } from "@/schemas/chat.schema";

interface ConfidenceCardProps {
  confidenceScores: ChatResponse["confidence_scores"];
  className?: string;
}

function AnimatedRing({ percentage, size = 72 }: { percentage: number; size?: number }) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;
  const color = percentage >= 80 ? "#10b981" : percentage >= 60 ? "#f59e0b" : "#ef4444";

  return (
    <svg width={size} height={size} className="-rotate-90" aria-hidden="true">
      <circle cx={size / 2} cy={size / 2} r={radius} fill="none" strokeWidth={6} stroke="currentColor" className="text-muted/30" />
      <motion.circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        strokeWidth={6}
        stroke={color}
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1, ease: "easeOut" }}
      />
    </svg>
  );
}

export const ConfidenceCard = memo(function ConfidenceCard({ confidenceScores, className }: ConfidenceCardProps) {
  const entries = Object.entries(confidenceScores ?? {});
  if (entries.length === 0) return null;

  // Compute overall
  const values = entries.map(([, v]) => (typeof v === "number" ? v : (v as { score?: number }).score ?? 0));
  const overall = Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 100);

  const label = overall >= 80 ? "High" : overall >= 60 ? "Moderate" : "Low";
  const labelColor = overall >= 80 ? "text-emerald-400" : overall >= 60 ? "text-amber-400" : "text-red-400";

  return (
    <div className={cn("rounded-xl border border-border/50 bg-card/50 p-4 space-y-4", className)}>
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">AI Confidence</h3>

      {/* Overall ring */}
      <div className="flex items-center gap-4">
        <div className="relative flex items-center justify-center">
          <AnimatedRing percentage={overall} />
          <span className="absolute text-sm font-bold">{overall}%</span>
        </div>
        <div>
          <p className={cn("text-sm font-semibold", labelColor)}>{label} Confidence</p>
          <p className="text-xs text-muted-foreground">across all agents</p>
        </div>
      </div>

      {/* Per-agent breakdown */}
      <div className="space-y-2">
        <AnimatePresence>
          {entries.map(([key, val]) => {
            const score = typeof val === "number" ? val : (val as { score?: number }).score ?? 0;
            const pct = Math.round(score * 100);
            const barColor = pct >= 80 ? "bg-emerald-500" : pct >= 60 ? "bg-amber-500" : "bg-red-500";
            return (
              <div key={key}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="capitalize text-muted-foreground">{key.replace(/_/g, " ")}</span>
                  <span className="font-medium">{pct}%</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-muted/40">
                  <motion.div
                    className={cn("h-full rounded-full", barColor)}
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                </div>
              </div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
});
