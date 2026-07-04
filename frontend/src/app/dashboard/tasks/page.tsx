import { PhysicianLayout } from "@/components/layout/physician-layout";

export default function ReviewQueuePage() {
  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10">
        <h1 className="text-2xl font-bold tracking-tight">Review Queue</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Queue placeholder. The list of flagged and low-confidence cases will appear here.
        </p>
      </div>
    </PhysicianLayout>
  );
}
