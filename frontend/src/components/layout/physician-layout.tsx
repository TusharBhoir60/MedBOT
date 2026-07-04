"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { ProtectedRoute } from "@/components/layout/protected-route";
import { ROLES } from "@/constants/roles";

export function PhysicianLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute requiredRole={ROLES.physician}>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar role="physician" />
        <div className="flex flex-1 flex-col overflow-hidden">
          <main className="flex-1 overflow-y-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
