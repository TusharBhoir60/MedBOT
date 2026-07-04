import { ReviewTaskResponse } from "@/schemas/review.schema";
import { BrainCircuit, ChevronRight } from "lucide-react";

export function AIAssessmentCard({ task }: { task: ReviewTaskResponse }) {
  const output = task.final_response || task.diagnosis_output || {};
  
  const conditions = Array.isArray(output.possible_conditions) ? output.possible_conditions : [];
  const nextStep = output.next_step;
  const analysis = output.analysis || {};
  const summary = analysis.summary || analysis.assessment || "No summary provided.";
  const recommendations = Array.isArray(analysis.recommendations) 
    ? analysis.recommendations 
    : (Array.isArray(analysis.recommended_actions) ? analysis.recommended_actions : []);

  return (
    <div className="rounded-xl border border-border/50 bg-card p-5 shadow-sm">
      <div className="flex items-center gap-2 border-b border-border/50 pb-3 mb-4">
        <BrainCircuit className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold tracking-tight">AI Assessment</h3>
      </div>

      <div className="space-y-6">
        {/* Conditions */}
        <div>
          <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-2">
            Differential Diagnoses
          </span>
          <div className="grid gap-2">
            {conditions.length > 0 ? conditions.map((c: unknown, i: number) => (
              <div key={i} className="flex items-start gap-2 rounded-lg border border-border/40 bg-muted/20 p-2.5">
                <ChevronRight className="mt-0.5 h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <div className="text-sm font-medium">
                  {typeof c === 'string' ? c : (c as Record<string, unknown>)?.name as string || JSON.stringify(c)}
                </div>
              </div>
            )) : (
              <p className="text-sm text-muted-foreground">None identified.</p>
            )}
          </div>
        </div>

        {/* Clinical Summary */}
        <div>
          <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-2">
            Clinical Summary
          </span>
          <p className="text-sm leading-relaxed text-card-foreground/90 bg-muted/10 p-3 rounded-lg border border-border/30">
            {summary}
          </p>
        </div>

        {/* Recommendations */}
        <div>
          <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-2">
            Recommended Actions
          </span>
          <ul className="list-disc space-y-1.5 pl-4 text-sm text-card-foreground/90">
            {recommendations.length > 0 ? recommendations.map((r: string, i: number) => (
              <li key={i} className="pl-1 marker:text-muted-foreground">{r}</li>
            )) : (
              <li className="text-muted-foreground list-none pl-0">No specific actions recommended.</li>
            )}
          </ul>
        </div>
        
        {/* Next Step */}
        {nextStep && (
          <div className="pt-2 border-t border-border/40">
            <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-1">
              Suggested Pipeline Route
            </span>
            <div className="inline-flex rounded-md bg-primary/10 px-2 py-1 text-xs font-semibold text-primary uppercase">
              {nextStep}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
