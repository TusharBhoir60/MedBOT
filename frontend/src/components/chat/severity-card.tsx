"use client";

import { memo } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle, Info, Flame } from "lucide-react";
import { cn } from "@/lib/utils";

type SeverityLevel = "low" | "medium" | "high" | "critical";

interface SeverityCardProps {
  escalationDecision: boolean;
  nextStep?: string;
  className?: string;
}

function getSeverity(escalated: boolean, nextStep?: string): SeverityLevel {
  if (escalated) return "critical";
  if (nextStep?.toLowerCase().includes("urgent")) return "high";
  if (nextStep?.toLowerCase().includes("follow")) return "medium";
  return "low";
}

const SEVERITY_CONFIG: Record<SeverityLevel, {
  label: string;
  description: string;
  icon: React.ElementType;
  ring: string;
  bg: string;
  text: string;
  bar: string;
  barWidth: string;
}> = {
  low: {
    label: "Low Severity",
    description: "Non-urgent — routine care recommended",
    icon: CheckCircle,
    ring: "ring-emerald-500/30",
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    bar: "bg-emerald-500",
    barWidth: "w-1/4",
  },
  medium: {
    label: "Moderate Severity",
    description: "Monitor symptoms — consult a doctor soon",
    icon: Info,
    ring: "ring-amber-500/30",
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    bar: "bg-amber-500",
    barWidth: "w-1/2",
  },
  high: {
    label: "High Severity",
    description: "Prompt medical attention recommended",
    icon: AlertTriangle,
    ring: "ring-orange-500/30",
    bg: "bg-orange-500/10",
    text: "text-orange-400",
    bar: "bg-orange-500",
    barWidth: "w-3/4",
  },
  critical: {
    label: "Critical — Escalated",
    description: "Immediate physician review required",
    icon: Flame,
    ring: "ring-red-500/30",
    bg: "bg-red-500/10",
    text: "text-red-400",
    bar: "bg-red-500",
    barWidth: "w-full",
  },
};

export const SeverityCard = memo(function SeverityCard({ escalationDecision, nextStep, className }: SeverityCardProps) {
  const severity = getSeverity(escalationDecision, nextStep);
  const config = SEVERITY_CONFIG[severity];
  const Icon = config.icon;

  return (
    <div className={cn("rounded-xl border border-border/50 bg-card/50 p-4 space-y-3", className)}>
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Severity</h3>

      <div className={cn("flex items-center gap-3 rounded-lg p-3 ring-1", config.bg, config.ring)}>
        <Icon className={cn("h-5 w-5 shrink-0", config.text)} />
        <div>
          <p className={cn("text-sm font-semibold", config.text)}>{config.label}</p>
          <p className="text-xs text-muted-foreground">{config.description}</p>
        </div>
      </div>

      {/* Severity bar */}
      <div>
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>Low</span>
          <span>Critical</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-muted/30">
          <motion.div
            className={cn("h-full rounded-full", config.bar)}
            initial={{ width: 0 }}
            animate={{ width: config.barWidth.replace("w-", "").replace("full", "100%").replace("1/4", "25%").replace("1/2", "50%").replace("3/4", "75%") }}
            style={{ width: severity === "low" ? "25%" : severity === "medium" ? "50%" : severity === "high" ? "75%" : "100%" }}
            transition={{ duration: 0.7, ease: "easeOut" }}
          />
        </div>
      </div>
    </div>
  );
});
