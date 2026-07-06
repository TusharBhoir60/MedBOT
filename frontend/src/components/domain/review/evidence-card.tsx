import { ReviewTaskResponse } from "@/schemas/review.schema";
import { BookOpen, FileText } from "lucide-react";

export function EvidenceCard({ task }: { task: ReviewTaskResponse }) {
  const output = task.final_response || task.diagnosis_output || {};
  
  // Try to find evidence, reasoning, or references in the AI output
  const reasoning = output.analysis?.reasoning || output.reasoning;
  const references = output.references || output.analysis?.references || [];

  if (!reasoning && (!references || references.length === 0)) {
    return null; // Don't render if there's no evidence data
  }

  return (
    <div className="rounded-xl border border-border/50 bg-card p-5 shadow-sm">
      <div className="flex items-center gap-2 border-b border-border/50 pb-3 mb-4">
        <BookOpen className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold tracking-tight">Clinical Evidence</h3>
      </div>

      <div className="space-y-5">
        {reasoning && (
          <div>
            <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
              <FileText className="h-3 w-3" /> Clinical Reasoning
            </span>
            <p className="text-sm leading-relaxed text-card-foreground/90 bg-muted/10 p-3 rounded-lg border border-border/30">
              {reasoning}
            </p>
          </div>
        )}

        {references && references.length > 0 && (
          <div>
            <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-2">
              References & Citations
            </span>
            <ul className="grid gap-2">
              {references.map((ref: unknown, i: number) => (
                <li key={i} className="flex items-start gap-2 text-sm text-card-foreground/80 bg-muted/20 p-2.5 rounded-lg border border-border/40">
                  <span className="text-xs font-mono text-muted-foreground mt-0.5">[{i+1}]</span>
                  <span>{typeof ref === 'string' ? ref : ((ref as Record<string, unknown>)?.title as string || JSON.stringify(ref))}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
