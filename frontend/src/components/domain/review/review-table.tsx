"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ReviewTaskResponse } from "@/schemas/review.schema";
import { Search, ChevronRight, Activity, ShieldAlert, CheckCircle2, Clock, CheckCircle } from "lucide-react";

interface ReviewTableProps {
  tasks: ReviewTaskResponse[];
}

export function ReviewTable({ tasks }: ReviewTableProps) {
  const [search, setSearch] = useState("");

  const filteredTasks = useMemo(() => {
    if (!search) return tasks;
    const lowerSearch = search.toLowerCase();
    return tasks.filter(t => 
      t.id.toLowerCase().includes(lowerSearch) || 
      t.session_id.toLowerCase().includes(lowerSearch) ||
      (t.assignee_id && t.assignee_id.toLowerCase().includes(lowerSearch))
    );
  }, [tasks, search]);

  const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
      case "NEW": return <Clock className="h-4 w-4 text-blue-500" />;
      case "ASSIGNED": return <Activity className="h-4 w-4 text-purple-500" />;
      case "UNDER_REVIEW": return <Activity className="h-4 w-4 text-purple-500 animate-pulse" />;
      case "APPROVED": return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "REJECTED": return <ShieldAlert className="h-4 w-4 text-red-500" />;
      case "OVERRIDDEN": return <CheckCircle className="h-4 w-4 text-amber-500" />;
      default: return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by ID, session, or assignee..."
            className="h-10 w-full rounded-md border border-input bg-transparent pl-9 pr-4 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>
      </div>

      <div className="rounded-md border border-border bg-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs text-muted-foreground">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Task ID</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Symptoms</th>
                <th className="px-4 py-3 text-left font-medium">Assignee</th>
                <th className="px-4 py-3 text-left font-medium">Created</th>
                <th className="px-4 py-3 text-right font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredTasks.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                    No tasks found matching your criteria.
                  </td>
                </tr>
              ) : (
                filteredTasks.map((task) => (
                  <tr key={task.id} className="group transition-colors hover:bg-muted/50">
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                      <Link href={`/dashboard/tasks/${task.id}`} className="hover:underline text-foreground">
                        {task.id.slice(0, 8)}...
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <StatusIcon status={task.status} />
                        <span className="text-xs font-medium capitalize">
                          {task.status.toLowerCase().replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {task.symptoms.slice(0, 2).map((sym, i) => (
                          <span key={i} className="inline-flex items-center rounded-sm bg-secondary px-1.5 py-0.5 text-[10px] font-medium text-secondary-foreground">
                            {sym}
                          </span>
                        ))}
                        {task.symptoms.length > 2 && (
                          <span className="inline-flex items-center rounded-sm bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                            +{task.symptoms.length - 2}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {task.assignee_id ? (
                        <div className="flex items-center gap-2">
                          <div className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary uppercase">
                            {task.assignee_id[0]}
                          </div>
                          <span className="text-xs">{task.assignee_id}</span>
                        </div>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {/* Note: since there's no created_at in the schema yet, we use a placeholder or ID extraction if it's an object ID. Using generic text for now. */}
                      Just now
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link 
                        href={`/dashboard/tasks/${task.id}`}
                        className="inline-flex items-center gap-1 rounded-md text-xs font-medium text-primary hover:underline"
                      >
                        Review
                        <ChevronRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
