"use client";

import Link from "next/link";
import { ShieldAlert, ArrowLeft } from "lucide-react";
import { ROUTES } from "@/constants/routes";

export default function UnauthorizedPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-error/10 text-error mb-6">
        <ShieldAlert className="h-8 w-8" />
      </div>
      <h1 className="text-3xl font-bold tracking-tight mb-2">Access Denied</h1>
      <p className="text-muted-foreground max-w-md mb-8">
        You do not have the required permissions to access this page. If you believe this is a mistake, please contact your administrator.
      </p>
      <Link
        href={ROUTES.home}
        className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
      >
        <ArrowLeft className="h-4 w-4" />
        Return Home
      </Link>
    </div>
  );
}
