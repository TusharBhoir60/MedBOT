"use client";

import { memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Tag, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface SymptomsPanelProps {
  symptoms: string[];
  extractedSymptoms?: Record<string, unknown>;
  onRemove?: (symptom: string) => void;
  className?: string;
}

export const SymptomsPanel = memo(function SymptomsPanel({
  symptoms,
  extractedSymptoms,
  onRemove,
  className,
}: SymptomsPanelProps) {
  const allSymptoms = Array.from(
    new Set([
      ...symptoms,
      ...Object.keys(extractedSymptoms ?? {}),
    ])
  ).filter(Boolean);

  return (
    <div className={cn("rounded-xl border border-border/50 bg-card/50 p-4 space-y-3", className)}>
      <div className="flex items-center gap-2">
        <Tag className="h-3.5 w-3.5 text-muted-foreground" />
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Reported Symptoms
        </h3>
        {allSymptoms.length > 0 && (
          <span className="ml-auto rounded-full bg-primary/20 px-2 py-0.5 text-xs font-medium text-primary">
            {allSymptoms.length}
          </span>
        )}
      </div>

      {allSymptoms.length === 0 ? (
        <p className="text-xs text-muted-foreground/60 italic">
          Symptoms will appear as you describe them…
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          <AnimatePresence>
            {allSymptoms.map((symptom) => (
              <motion.span
                key={symptom}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.2 }}
                className="group inline-flex items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-medium text-primary"
              >
                {symptom}
                {onRemove && (
                  <button
                    onClick={() => onRemove(symptom)}
                    className="ml-0.5 rounded-full opacity-0 transition-opacity group-hover:opacity-100"
                    aria-label={`Remove symptom ${symptom}`}
                  >
                    <X className="h-3 w-3 text-primary/60 hover:text-primary" />
                  </button>
                )}
              </motion.span>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
});
