import { ReviewTaskResponse } from "@/schemas/review.schema";
import { ArrowLeft, Clock, Activity, CheckCircle2, ShieldAlert, CheckCircle } from "lucide-react";
import Link from "next/link";

interface TaskHeaderProps {
  task: ReviewTaskResponse;
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "NEW": return <Clock className="h-4 w-4 text-blue-500" />;
    case "ASSIGNED": return <Activity className="h-4 w-4 text-purple-500" />;
    case "UNDER_REVIEW": return <Activity className="h-4 w-4 text-purple-500 animate-pulse" />;
    case "APPROVED": return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case "REJECTED": return <ShieldAlert className="h-4 w-4 text-red-500" />;
    case "OVERRIDDEN": return <CheckCircle className="h-4 w-4 text-amber-500" />;
    default: return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

export function TaskHeader({ task }: TaskHeaderProps) {

  return (
    <div className="flex flex-col gap-4 border-b border-border/50 pb-4">
      {/* Breadcrumb */}
      <Link href="/dashboard/tasks" className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground hover:underline">
        <ArrowLeft className="h-3 w-3" />
        Back to Queue
      </Link>

      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold tracking-tight">Review Task</h1>
            <div className="flex items-center gap-1.5 rounded-full border border-border bg-card px-2.5 py-0.5 shadow-sm">
              <StatusIcon status={task.status} />
              <span className="text-xs font-medium capitalize">{task.status.toLowerCase().replace('_', ' ')}</span>
            </div>
          </div>
          <p className="mt-1 font-mono text-xs text-muted-foreground">ID: {task.id}</p>
        </div>

        {/* Assignee Badge */}
        <div className="flex flex-col items-end gap-1">
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">Assignee</span>
          {task.assignee_id ? (
            <div className="flex items-center gap-2 rounded-md border border-border bg-card px-2.5 py-1 shadow-sm">
              <div className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary uppercase">
                {task.assignee_id[0]}
              </div>
              <span className="text-xs font-medium">{task.assignee_id}</span>
            </div>
          ) : (
            <span className="inline-flex items-center rounded-md border border-dashed border-border bg-muted/50 px-2.5 py-1 text-xs font-medium text-muted-foreground">
              Unassigned
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
