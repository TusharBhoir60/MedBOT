"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { Activity, Eye, EyeOff, Loader2, AlertCircle } from "lucide-react";
import { authService } from "@/services/auth.service";
import { useAuth } from "@/providers/auth-provider";
import { ROUTES } from "@/constants/routes";
import { LoginRequestSchema, type LoginRequest } from "@/schemas/auth.schema";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginRequest>({
    resolver: zodResolver(LoginRequestSchema),
    defaultValues: { username: "", password: "" },
  });

  const onSubmit = async (data: LoginRequest) => {
    setServerError(null);
    try {
      const response = await authService.login(data);
      // Wait for AuthProvider to decode and set state
      login(response.access_token, {
        sub: data.username,
        roles: ["physician"], // Simplified for mock; real payload decoded in AuthProvider
      });
      router.push(ROUTES.dashboard);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Invalid credentials. Please try again.";
      setServerError(msg);
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
          <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">Sign in to your clinical workspace</p>
        </div>

        {/* Login Card */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm sm:p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            {serverError && (
              <div className="flex items-center gap-2 rounded-md bg-error/10 p-3 text-sm text-error">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <p>{serverError}</p>
              </div>
            )}

            <div className="space-y-1.5">
              <label htmlFor="username" className="text-sm font-medium">
                Username or Email
              </label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                autoFocus
                {...register("username")}
                className={`flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 transition-colors ${
                  errors.username ? "border-error focus-visible:ring-error/20" : "border-input focus-visible:ring-primary/20"
                }`}
                placeholder="Enter your username"
              />
              {errors.username && <p className="text-xs text-error">{errors.username.message}</p>}
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <a href="#" className="text-xs font-medium text-primary hover:underline">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  {...register("password")}
                  className={`flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 transition-colors ${
                    errors.password ? "border-error focus-visible:ring-error/20" : "border-input focus-visible:ring-primary/20"
                  }`}
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-error">{errors.password.message}</p>}
            </div>

            <div className="flex items-center space-x-2 pt-1 pb-2">
              <input
                type="checkbox"
                id="remember"
                className="h-4 w-4 rounded border-input text-primary focus:ring-primary/20"
              />
              <label
                htmlFor="remember"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Remember me for 30 days
              </label>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
