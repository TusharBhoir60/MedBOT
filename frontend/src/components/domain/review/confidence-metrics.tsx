import { ReviewTaskResponse } from "@/schemas/review.schema";
import { Gauge, ShieldAlert } from "lucide-react";

export function ConfidenceMetrics({ task }: { task: ReviewTaskResponse }) {
  const output = task.final_response || task.diagnosis_output || {};
  const scores = output.confidence_scores || {};
  const escalation = output.escalation_decision;

  const vals = Object.values(scores).map(Number).filter(Boolean);
  const overall = vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  
  if (Object.keys(scores).length === 0) return null;

  return (
    <div className="rounded-xl border border-border/50 bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between border-b border-border/50 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <Gauge className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold tracking-tight">Confidence Metrics</h3>
        </div>
        {escalation && (
          <div className="flex items-center gap-1.5 rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-semibold text-red-500">
            <ShieldAlert className="h-3 w-3" />
            Escalation Triggered
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Overall Ring */}
        <div className="col-span-1 flex flex-col items-center justify-center border-r border-border/50 pr-6">
          <div className="relative flex h-24 w-24 items-center justify-center">
            <svg className="h-full w-full -rotate-90 transform" viewBox="0 0 100 100">
              <circle
                className="text-muted/30"
                strokeWidth="8"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
              />
              <circle
                className={overall > 0.8 ? "text-green-500" : overall > 0.5 ? "text-amber-500" : "text-red-500"}
                strokeWidth="8"
                strokeDasharray={`${overall * 251.2} 251.2`}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-2xl font-bold">{Math.round(overall * 100)}%</span>
            </div>
          </div>
          <span className="mt-3 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">Overall</span>
        </div>

        {/* Breakdown */}
        <div className="col-span-2 space-y-3">
          {Object.entries(scores).map(([key, value]) => {
            const num = Number(value);
            return (
              <div key={key}>
                <div className="mb-1 flex justify-between text-xs">
                  <span className="font-medium capitalize text-card-foreground/80">{key.replace(/_/g, ' ')}</span>
                  <span className="text-muted-foreground">{Math.round(num * 100)}%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted/30">
                  <div
                    className={`h-full rounded-full transition-all duration-1000 ${
                      num > 0.8 ? "bg-green-500" : num > 0.5 ? "bg-amber-500" : "bg-red-500"
                    }`}
                    style={{ width: `${Math.max(5, num * 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
