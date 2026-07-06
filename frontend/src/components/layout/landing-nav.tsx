"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Activity, Menu, X, Sun, Moon } from "lucide-react";
import { useState } from "react";
import { useTheme } from "next-themes";
import { ROUTES } from "@/constants/routes";

const navLinks = [
  { href: "#how-it-works", label: "How It Works" },
  { href: "#cmar", label: "Technology" },
  { href: "#features", label: "Features" },
  { href: "#safety", label: "Safety" },
];

export function LandingNav() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="fixed top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-md"
    >
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link href={ROUTES.home} className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          <span className="text-sm font-semibold tracking-tight">AarogyaAgent</span>
          <span className="rounded-sm bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">v2</span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-6" aria-label="Main navigation">
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {l.label}
            </a>
          ))}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
            className="rounded-md p-2 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          <Link
            href={ROUTES.login}
            className="hidden md:inline-flex h-8 items-center rounded-md border border-border bg-background px-3 text-xs font-medium text-foreground hover:bg-muted transition-colors"
          >
            Physician Login
          </Link>
          <Link
            href={ROUTES.chat}
            className="hidden md:inline-flex h-8 items-center rounded-md bg-primary px-3 text-xs font-medium text-primary-foreground hover:opacity-90 transition-opacity"
          >
            Start Assessment
          </Link>
          <button
            className="md:hidden p-2 text-muted-foreground"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="md:hidden border-t border-border bg-background px-4 py-4 space-y-3"
        >
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setMobileOpen(false)}
              className="block text-sm text-muted-foreground hover:text-foreground"
            >
              {l.label}
            </a>
          ))}
          <div className="flex gap-2 pt-2">
            <Link href={ROUTES.login} className="flex-1 text-center h-9 flex items-center justify-center rounded-md border border-border text-sm text-foreground">
              Physician Login
            </Link>
            <Link href={ROUTES.chat} className="flex-1 text-center h-9 flex items-center justify-center rounded-md bg-primary text-sm text-primary-foreground">
              Start Assessment
            </Link>
          </div>
        </motion.div>
      )}
    </motion.header>
  );
}
