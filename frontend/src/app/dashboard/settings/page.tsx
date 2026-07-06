import { PhysicianLayout } from "@/components/layout/physician-layout";

export default function SettingsPage() {
  return (
    <PhysicianLayout>
      <div className="p-6 sm:p-10">
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Settings placeholder. Profile and preference management will be located here.
        </p>
      </div>
    </PhysicianLayout>
  );
}
