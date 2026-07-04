"use client";

import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface MedicalDisclaimerProps {
  compact?: boolean;
  className?: string;
}

export function MedicalDisclaimer({ compact = false, className }: MedicalDisclaimerProps) {
  return (
    <div
      className={cn(
        "flex items-start gap-2 rounded-lg border border-border/40 bg-muted/30 text-muted-foreground",
        compact ? "px-3 py-2 text-xs" : "px-4 py-3 text-sm",
        className
      )}
      role="note"
      aria-label="Medical disclaimer"
    >
      <ShieldCheck className={cn("shrink-0 mt-0.5", compact ? "h-3.5 w-3.5" : "h-4 w-4")} />
      <p>
        This AI assessment is for informational purposes only and does not replace professional
        medical advice. Always consult a qualified physician for diagnosis and treatment.
      </p>
    </div>
  );
}
