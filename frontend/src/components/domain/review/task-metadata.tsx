import { ReviewTaskResponse } from "@/schemas/review.schema";
import { Info, Calendar } from "lucide-react";

export function TaskMetadata({ task }: { task: ReviewTaskResponse }) {
  // Since we don't have explicit created_at/updated_at in the mock schema, we'll use static values for UI visualization purposes, or use the current time as a fallback for "just now".
  return (
    <div className="rounded-xl border border-border/50 bg-card p-4 shadow-sm">
      <div className="flex items-center gap-2 border-b border-border/50 pb-3 mb-3">
        <Info className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold tracking-tight">Metadata</h3>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Session ID</span>
          <span className="font-mono text-card-foreground/80">{task.session_id.slice(0, 8)}...</span>
        </div>
        
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground flex items-center gap-1"><Calendar className="h-3 w-3" /> Created</span>
          <span className="text-card-foreground/80">Just now</span>
        </div>
        
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground flex items-center gap-1"><Calendar className="h-3 w-3" /> Updated</span>
          <span className="text-card-foreground/80">Just now</span>
        </div>
      </div>
    </div>
  );
}
