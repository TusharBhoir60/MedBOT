import { PhysicianLayout } from "@/components/layout/physician-layout";

export default function DashboardPage() {
  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10">
        <h1 className="text-2xl font-bold tracking-tight">Physician Dashboard</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Dashboard content placeholder. Overview metrics and activity will be displayed here.
        </p>
      </div>
    </PhysicianLayout>
  );
}
