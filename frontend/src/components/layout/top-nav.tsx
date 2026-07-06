"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Sun, Moon, Menu, ChevronRight, LogOut, Settings } from "lucide-react";
import { useTheme } from "next-themes";
import { useAuth } from "@/providers/auth-provider";
import { cn } from "@/lib/utils";
import { useState, useRef, useEffect } from "react";

export function TopNav({ className, onMenuClick }: { className?: string; onMenuClick?: () => void }) {
  const { theme, setTheme } = useTheme();
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Generate breadcrumbs from pathname
  const paths = pathname.split("/").filter(Boolean);
  const breadcrumbs = paths.map((path, i) => {
    const href = "/" + paths.slice(0, i + 1).join("/");
    const label = path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, " ");
    return { href, label, isLast: i === paths.length - 1 };
  });

  return (
    <header
      className={cn(
        "sticky top-0 z-40 flex h-14 shrink-0 items-center gap-4 border-b border-border bg-background/80 px-4 backdrop-blur-sm sm:px-6",
        className
      )}
    >
      <button
        onClick={onMenuClick}
        className="md:hidden -ml-2 rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
        aria-label="Toggle menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Breadcrumbs */}
      <nav className="hidden sm:flex items-center text-sm font-medium text-muted-foreground" aria-label="Breadcrumb">
        {breadcrumbs.map((crumb, i) => (
          <div key={crumb.href} className="flex items-center">
            {i > 0 && <ChevronRight className="mx-2 h-4 w-4 shrink-0 text-muted-foreground/50" />}
            {crumb.isLast ? (
              <span className="text-foreground" aria-current="page">{crumb.label}</span>
            ) : (
              <Link href={crumb.href} className="hover:text-foreground transition-colors">
                {crumb.label}
              </Link>
            )}
          </div>
        ))}
        {breadcrumbs.length === 0 && <span className="text-foreground">Home</span>}
      </nav>

      <div className="ml-auto flex items-center gap-1.5 sm:gap-3">
        <button
          aria-label="Notifications"
          className="relative rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          <Bell className="h-4.5 w-4.5 h-[18px] w-[18px]" />
          <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-primary" />
        </button>

        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          aria-label="Toggle theme"
          className="rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          {theme === "dark" ? <Sun className="h-4.5 w-4.5 h-[18px] w-[18px]" /> : <Moon className="h-4.5 w-4.5 h-[18px] w-[18px]" />}
        </button>

        <div className="relative ml-1" ref={profileRef}>
          <button
            onClick={() => setProfileOpen(!profileOpen)}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary uppercase transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            {user?.sub?.[0] ?? "U"}
          </button>

          {/* Profile Dropdown */}
          {profileOpen && (
            <div className="absolute right-0 top-full mt-2 w-56 rounded-md border border-border bg-popover text-popover-foreground shadow-md outline-none animate-in fade-in zoom-in-95 duration-200">
              <div className="flex flex-col space-y-1 p-4 border-b border-border">
                <p className="text-sm font-medium leading-none">{user?.sub ?? "User"}</p>
                <p className="text-xs leading-none text-muted-foreground capitalize">
                  {user?.roles?.[0] ?? "Guest"}
                </p>
              </div>
              <div className="p-1">
                <Link
                  href="/dashboard/settings"
                  onClick={() => setProfileOpen(false)}
                  className="relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                >
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </Link>
                <button
                  onClick={() => {
                    setProfileOpen(false);
                    logout();
                  }}
                  className="relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
