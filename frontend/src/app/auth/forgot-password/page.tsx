"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { authService } from "@/services/auth.service";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [resetToken, setResetToken] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);
    setSuccessMessage(null);
    setResetToken(null);
    setIsSubmitting(true);
    
    if (!username.trim()) {
      setServerError("Username is required");
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await authService.forgotPassword(username);
      setSuccessMessage(response.message);
      if (response.reset_token) {
        setResetToken(response.reset_token);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to request password reset.";
      setServerError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-muted/30 p-4 sm:p-8">
      <div className="w-full max-w-[400px]">
        {/* Brand Header */}
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Activity className="h-6 w-6 text-primary" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">Forgot Password</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">Enter your username to reset your password</p>
        </div>

        {/* Forgot Password Card */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm sm:p-8">
          {successMessage ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 rounded-md bg-primary/10 p-3 text-sm text-primary">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <p>{successMessage}</p>
              </div>
              
              {/* For development purposes only: show the token so we can use it to reset */}
              {resetToken && (
                <div className="rounded-md border p-3 text-xs">
                  <p className="font-semibold mb-1">Development Mode - Reset Link:</p>
                  <a href={`/auth/reset-password?token=${resetToken}`} className="text-primary hover:underline break-all">
                    Click here to reset your password
                  </a>
                </div>
              )}
              
              <button
                onClick={() => router.push("/auth/login")}
                className="mt-4 inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                Return to Sign In
              </button>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="space-y-4" noValidate>
              {serverError && (
                <div className="flex items-center gap-2 rounded-md bg-error/10 p-3 text-sm text-error">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <p>{serverError}</p>
                </div>
              )}

              <div className="space-y-1.5">
                <label htmlFor="username" className="text-sm font-medium">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  autoComplete="username"
                  autoFocus
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                  placeholder="Enter your username"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  "Send Reset Link"
                )}
              </button>
            </form>
          )}
          
          {!successMessage && (
            <div className="mt-4 text-center text-sm">
              Remember your password?{" "}
              <a href="/auth/login" className="text-primary hover:underline font-medium">
                Sign in
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
