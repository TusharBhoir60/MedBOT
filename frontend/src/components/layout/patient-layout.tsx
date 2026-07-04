"use client";

import { TopNav } from "@/components/layout/top-nav";

export function PatientLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      <TopNav />
      <main className="flex flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
}
