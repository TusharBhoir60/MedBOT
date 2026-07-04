import { ReviewTaskResponse } from "@/schemas/review.schema";
import { CheckCircle2, ShieldAlert, Edit, UserPlus } from "lucide-react";
import { useReviewActions } from "@/hooks/use-review";
import { useState } from "react";
import { ActionDialogs } from "./action-dialogs";

export function ReviewActionBar({ task }: { task: ReviewTaskResponse }) {
  const { assignTask, approveTask } = useReviewActions(task.id);
  
  const [rejectOpen, setRejectOpen] = useState(false);
  const [overrideOpen, setOverrideOpen] = useState(false);

  const isAssigned = !!task.assignee_id;
  const isPendingAction = task.status !== "APPROVED" && task.status !== "REJECTED" && task.status !== "OVERRIDDEN";

  if (!isPendingAction) {
    return null;
  }

  return (
    <>
      <div className="sticky bottom-0 z-10 flex items-center justify-between border-t border-border/50 bg-background/80 px-6 py-4 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center gap-2">
          {!isAssigned && (
            <button
              onClick={() => assignTask.mutate()}
              disabled={assignTask.isPending}
              className="inline-flex items-center gap-2 rounded-md bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground shadow-sm hover:bg-secondary/80 disabled:opacity-50"
            >
              <UserPlus className="h-4 w-4" /> Assign to Me
            </button>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setRejectOpen(true)}
            disabled={!isAssigned}
            className="inline-flex items-center gap-2 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-500 shadow-sm hover:bg-red-500/20 disabled:opacity-50"
          >
            <ShieldAlert className="h-4 w-4" /> Reject
          </button>
          
          <button
            onClick={() => setOverrideOpen(true)}
            disabled={!isAssigned}
            className="inline-flex items-center gap-2 rounded-md border border-amber-500/20 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-500 shadow-sm hover:bg-amber-500/20 disabled:opacity-50"
          >
            <Edit className="h-4 w-4" /> Override
          </button>
          
          <button
            onClick={() => approveTask.mutate()}
            disabled={approveTask.isPending || !isAssigned}
            className="inline-flex items-center gap-2 rounded-md bg-green-500 px-6 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-600 disabled:opacity-50"
          >
            <CheckCircle2 className="h-4 w-4" /> Approve Assessment
          </button>
        </div>
      </div>

      <ActionDialogs
        task={task}
        rejectOpen={rejectOpen}
        onRejectClose={() => setRejectOpen(false)}
        overrideOpen={overrideOpen}
        onOverrideClose={() => setOverrideOpen(false)}
      />
    </>
  );
}
