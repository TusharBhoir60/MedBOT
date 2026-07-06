"use client";

import { PhysicianLayout } from "@/components/layout/physician-layout";
import { ReviewTable } from "@/components/domain/review/review-table";
import { useReviewQueue } from "@/hooks/use-review";
import { ListTodo, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

export default function ReviewQueuePage() {
  const { data: tasks, isLoading, isError, refetch, isFetching } = useReviewQueue();

  return (
    <PhysicianLayout>
      <div className="flex h-full flex-col overflow-hidden">
        {/* Header */}
        <header className="flex shrink-0 items-center justify-between border-b border-border/50 bg-background/95 px-6 py-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <ListTodo className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">Review Queue</h1>
              <p className="text-xs text-muted-foreground">Manage and validate AI clinical assessments.</p>
            </div>
          </div>
          <button 
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 rounded-md border border-input bg-transparent px-3 py-1.5 text-xs font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-border">
          {isLoading ? (
            <div className="flex h-40 flex-col items-center justify-center gap-2">
              <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Loading queue...</p>
            </div>
          ) : isError ? (
            <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 text-red-500">
              <p className="text-sm font-medium">Failed to load the review queue.</p>
              <button onClick={() => refetch()} className="text-xs underline hover:text-red-400">Try again</button>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="mx-auto max-w-6xl"
            >
              <ReviewTable tasks={tasks || []} />
            </motion.div>
          )}
        </main>
      </div>
    </PhysicianLayout>
  );
}
