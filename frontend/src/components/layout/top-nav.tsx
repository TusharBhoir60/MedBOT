"use client";

import Link from "next/link";
import { Activity, Sun, Moon } from "lucide-react";
import { useTheme } from "next-themes";
import { ROUTES } from "@/constants/routes";
import { cn } from "@/lib/utils";

export function TopNav({ className }: { className?: string }) {
  const { theme, setTheme } = useTheme();

  return (
    <header
      className={cn(
        "sticky top-0 z-40 flex h-14 w-full items-center gap-4 border-b border-border bg-background/80 px-4 backdrop-blur-sm",
        className
      )}
    >
      <Link href={ROUTES.home} className="flex items-center gap-2 font-semibold">
        <Activity className="h-5 w-5 text-primary" />
        <span className="text-sm tracking-tight">AarogyaAgent</span>
      </Link>

      <div className="ml-auto flex items-center gap-2">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          aria-label="Toggle theme"
          className="rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>
      </div>
    </header>
  );
}
