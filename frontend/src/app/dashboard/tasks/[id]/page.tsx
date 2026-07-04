"use client";

import { use } from "react";
import { PhysicianLayout } from "@/components/layout/physician-layout";
import { useReviewTask } from "@/hooks/use-review";
import { TaskHeader } from "@/components/domain/review/task-header";
import { PatientOverview } from "@/components/domain/review/patient-overview";
import { AIAssessmentCard } from "@/components/domain/review/ai-assessment-card";
import { EvidenceCard } from "@/components/domain/review/evidence-card";
import { ConfidenceMetrics } from "@/components/domain/review/confidence-metrics";
import { TaskMetadata } from "@/components/domain/review/task-metadata";
import { CommentPanel } from "@/components/domain/review/comment-panel";
import { ReviewActionBar } from "@/components/domain/review/review-action-bar";
import { RefreshCw, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function ReviewTaskPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const taskId = resolvedParams.id;
  const { data: task, isLoading, isError, refetch } = useReviewTask(taskId);

  return (
    <PhysicianLayout>
      {isLoading ? (
        <div className="flex h-full flex-col items-center justify-center gap-2">
          <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Loading task details...</p>
        </div>
      ) : isError || !task ? (
        <div className="flex h-full flex-col items-center justify-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-red-500">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <p className="text-sm font-medium">Failed to load task details.</p>
          <div className="flex gap-4">
            <button onClick={() => refetch()} className="text-sm text-primary hover:underline">Try again</button>
            <Link href="/dashboard/tasks" className="text-sm text-muted-foreground hover:underline">Return to Queue</Link>
          </div>
        </div>
      ) : (
        <div className="flex h-full flex-col">
          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-border">
            <div className="mx-auto max-w-[1400px] p-6">
              <TaskHeader task={task} />
              
              <div className="mt-6 flex flex-col gap-6 lg:flex-row lg:items-start">
                {/* Main Column */}
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="flex flex-1 flex-col gap-6 min-w-0"
                >
                  <PatientOverview task={task} />
                  <ConfidenceMetrics task={task} />
                  <AIAssessmentCard task={task} />
                  <EvidenceCard task={task} />
                </motion.div>

                {/* Right Sidebar */}
                <motion.div 
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                  className="flex w-full shrink-0 flex-col gap-6 lg:w-[380px]"
                >
                  <TaskMetadata task={task} />
                  <div className="h-[500px]">
                    <CommentPanel task={task} />
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
          <ReviewActionBar task={task} />
        </div>
      )}
    </PhysicianLayout>
  );
}
