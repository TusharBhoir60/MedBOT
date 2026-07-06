"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-error/10 text-error mb-6">
        <AlertTriangle className="h-8 w-8" />
      </div>
      <h1 className="text-3xl font-bold tracking-tight mb-2">Something went wrong!</h1>
      <p className="text-muted-foreground max-w-md mb-8">
        An unexpected error occurred. Our team has been notified.
      </p>
      <button
        onClick={() => reset()}
        className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
      >
        <RefreshCcw className="h-4 w-4" />
        Try again
      </button>
    </div>
  );
}
