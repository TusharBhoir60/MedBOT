"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";
import { ROUTES } from "@/constants/routes";
import {
  LayoutDashboard,
  MessageSquareHeart,
  Settings,
  LogOut,
  ChevronRight,
  Activity,
} from "lucide-react";

const physicianNavItems = [
  { href: ROUTES.dashboard, label: "Review Queue", icon: LayoutDashboard },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

const patientNavItems = [
  { href: ROUTES.chat, label: "AI Triage Chat", icon: MessageSquareHeart },
];

interface SidebarProps {
  role: "physician" | "patient";
}

export function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();
  const { logout, user } = useAuth();
  const items = role === "physician" ? physicianNavItems : patientNavItems;

  return (
    <aside className="flex h-full w-60 flex-col border-r border-border bg-sidebar">
      {/* Logo */}
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <Activity className="h-5 w-5 text-primary" />
        <span className="text-sm font-semibold tracking-tight">AarogyaAgent</span>
        <span className="ml-1 rounded-sm bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">v2</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 p-2">
        {items.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span>{label}</span>
              {isActive && <ChevronRight className="ml-auto h-3 w-3 opacity-50" />}
            </Link>
          );
        })}
      </nav>

      {/* User footer */}
      <div className="border-t border-border p-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary uppercase">
            {user?.sub?.[0] ?? "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate text-xs font-medium">{user?.sub ?? "User"}</p>
            <p className="truncate text-[10px] text-muted-foreground capitalize">{user?.roles?.[0] ?? "—"}</p>
          </div>
          <button
            onClick={logout}
            aria-label="Logout"
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <LogOut className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
