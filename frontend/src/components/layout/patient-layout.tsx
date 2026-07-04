"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { TopNav } from "@/components/layout/top-nav";
import { ProtectedRoute } from "@/components/layout/protected-route";
import { useState } from "react";
import { cn } from "@/lib/utils";

export function PatientLayout({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Desktop Sidebar */}
        <div className="hidden md:block">
          <Sidebar role="patient" />
        </div>

        {/* Mobile Sidebar overlay */}
        {mobileMenuOpen && (
          <div
            className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm md:hidden"
            onClick={() => setMobileMenuOpen(false)}
          >
            <div
              className="fixed inset-y-0 left-0 z-50 w-3/4 max-w-sm shadow-lg animate-in slide-in-from-left-full"
              onClick={(e) => e.stopPropagation()}
            >
              <Sidebar role="patient" className="w-full" onNavigate={() => setMobileMenuOpen(false)} />
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <TopNav onMenuClick={() => setMobileMenuOpen(true)} />
          <main className="flex-1 overflow-y-auto">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
