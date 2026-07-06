import { PhysicianLayout } from "@/components/layout/physician-layout";

export default function AnalyticsPage() {
  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10">
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Analytics placeholder. System performance and case distribution metrics will be displayed here.
        </p>
      </div>
    </PhysicianLayout>
  );
}
