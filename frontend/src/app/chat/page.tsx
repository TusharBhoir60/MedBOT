import { PatientLayout } from "@/components/layout/patient-layout";

export default function ChatPage() {
  return (
    <PatientLayout>
      <div className="flex h-full flex-col items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">Patient Assessment</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Chat interface placeholder. Functionality will be implemented in the next sprint.
          </p>
        </div>
      </div>
    </PatientLayout>
  );
}
