import { ReviewTaskResponse } from "@/schemas/review.schema";
import { User, HeartPulse } from "lucide-react";

export function PatientOverview({ task }: { task: ReviewTaskResponse }) {
  const info = task.patient_info;
  const gender = info?.gender || "Unknown";
  const age = info?.age || "Unknown";
  
  return (
    <div className="rounded-xl border border-border/50 bg-card p-5 shadow-sm">
      <div className="flex items-center gap-2 border-b border-border/50 pb-3 mb-3">
        <User className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold tracking-tight">Patient Context</h3>
      </div>
      
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-1">
            Demographics
          </span>
          <p className="text-sm">
            {age} {typeof age === 'number' ? 'yrs' : ''} • <span className="capitalize">{gender}</span>
          </p>
        </div>
        
        <div>
          <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground mb-1 flex items-center gap-1.5">
            <HeartPulse className="h-3 w-3" /> Reported Symptoms
          </span>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {task.symptoms.length > 0 ? task.symptoms.map((s, i) => (
              <span key={i} className="inline-flex items-center rounded-sm bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
                {s}
              </span>
            )) : (
              <span className="text-xs text-muted-foreground">None explicitly provided</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
