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
  ListTodo,
  BarChart3,
  ShieldAlert,
} from "lucide-react";
import { ROLES } from "@/constants/roles";

type NavItem = { href: string; label: string; icon: React.ElementType };

const physicianNavItems: NavItem[] = [
  { href: ROUTES.dashboard, label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/tasks", label: "Review Queue", icon: ListTodo },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
];

const patientNavItems: NavItem[] = [
  { href: ROUTES.chat, label: "Chat", icon: MessageSquareHeart },
];

const adminNavItems: NavItem[] = [
  { href: "/admin/system", label: "System Config", icon: ShieldAlert },
];

interface SidebarProps {
  role: "physician" | "patient" | "admin";
  className?: string;
  onNavigate?: () => void;
}

export function Sidebar({ role, className, onNavigate }: SidebarProps) {
  const pathname = usePathname();
  const { logout, user } = useAuth();
  
  let items: NavItem[] = patientNavItems;
  if (role === ROLES.physician) items = physicianNavItems;
  if (role === ROLES.admin) items = adminNavItems;

  return (
    <aside className={cn("flex h-full w-60 flex-col border-r border-border bg-sidebar", className)}>
      {/* Logo */}
      <div className="flex h-14 shrink-0 items-center gap-2 border-b border-border px-4">
        <Activity className="h-5 w-5 text-primary" />
        <span className="text-sm font-semibold tracking-tight">AarogyaAgent</span>
        <span className="ml-1 rounded-sm bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">v2</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 p-2 overflow-y-auto">
        {items.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              onClick={onNavigate}
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
      <div className="shrink-0 border-t border-border p-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary uppercase">
            {user?.sub?.[0] ?? "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate text-xs font-medium">{user?.sub ?? "User"}</p>
            <p className="truncate text-[10px] text-muted-foreground capitalize">{user?.roles?.[0] ?? "—"}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
