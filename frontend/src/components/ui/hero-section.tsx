"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, Sparkles } from "lucide-react";
import { ROUTES } from "@/constants/routes";
import { staggerContainer, fadeUp } from "@/components/ui/motion";

function HeroOrb() {
  return (
    <div className="relative mx-auto w-full max-w-lg aspect-square" aria-hidden="true">
      {/* Outer glow ring */}
      <motion.div
        className="absolute inset-0 rounded-full border border-primary/10 bg-gradient-to-br from-primary/5 to-transparent"
        animate={{ scale: [1, 1.04, 1], opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      />
      {/* Middle ring */}
      <motion.div
        className="absolute inset-[10%] rounded-full border border-primary/15 bg-gradient-to-br from-primary/8 to-transparent"
        animate={{ scale: [1, 1.02, 1], opacity: [0.8, 1, 0.8] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
      />
      {/* Core */}
      <div className="absolute inset-[22%] rounded-full bg-gradient-to-br from-primary/20 via-primary/10 to-transparent flex items-center justify-center">
        <div className="flex flex-col items-center gap-1">
          <Sparkles className="h-8 w-8 text-primary/60" />
          <span className="text-[10px] font-medium text-muted-foreground tracking-wider">CMAR v2</span>
        </div>
      </div>

      {/* Orbiting node: Intake */}
      <AgentNode label="Intake" angle={-30} color="bg-info/20 text-info border-info/30" delay={0} />
      <AgentNode label="Symptom" angle={60} color="bg-warning/20 text-warning border-warning/30" delay={0.3} />
      <AgentNode label="Diagnosis" angle={150} color="bg-primary/20 text-primary border-primary/30" delay={0.6} />
      <AgentNode label="Review" angle={240} color="bg-success/20 text-success border-success/30" delay={0.9} />
    </div>
  );
}

function AgentNode({ label, angle, color, delay }: { label: string; angle: number; color: string; delay: number }) {
  const rad = (angle * Math.PI) / 180;
  const r = 44; // percentage radius
  const x = 50 + r * Math.cos(rad);
  const y = 50 + r * Math.sin(rad);
  return (
    <motion.div
      className={`absolute -translate-x-1/2 -translate-y-1/2 rounded-full border px-2.5 py-1 text-[10px] font-medium backdrop-blur-sm ${color}`}
      style={{ left: `${x}%`, top: `${y}%` }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: delay + 0.8 }}
    >
      {label}
    </motion.div>
  );
}

export function HeroSection() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden pt-14">
      {/* Background gradient */}
      <div
        className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-b from-primary/5 via-background to-background"
        aria-hidden="true"
      />
      {/* Grid overlay */}
      <div
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.03] dark:opacity-[0.06]"
        style={{
          backgroundImage: `linear-gradient(to right, hsl(var(--foreground) / 1) 1px, transparent 1px), linear-gradient(to bottom, hsl(var(--foreground) / 1) 1px, transparent 1px)`,
          backgroundSize: "48px 48px",
        }}
        aria-hidden="true"
      />

      <div className="mx-auto w-full max-w-6xl px-4 sm:px-6 py-24 lg:py-0">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          {/* Text */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="show"
            className="flex flex-col gap-6 text-center lg:text-left"
          >
            <motion.div variants={fadeUp}>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary">
                <ShieldCheck className="h-3 w-3" />
                Human-validated · Research-grade AI
              </span>
            </motion.div>

            <motion.h1
              variants={fadeUp}
              className="text-4xl font-bold leading-[1.15] tracking-tight sm:text-5xl lg:text-6xl"
            >
              AI-powered triage.{" "}
              <span className="bg-gradient-to-r from-primary to-primary/50 bg-clip-text text-transparent">
                Physician-trusted.
              </span>
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="text-base text-muted-foreground sm:text-lg leading-relaxed max-w-lg mx-auto lg:mx-0"
            >
              AarogyaAgent uses a multi-agent reasoning system to analyze your symptoms, generate confidence-weighted
              differential diagnoses, and flag high-complexity cases for physician review — in seconds.
            </motion.p>

            <motion.div variants={fadeUp} className="flex flex-wrap items-center gap-3 justify-center lg:justify-start">
              <Link
                href={ROUTES.chat}
                className="group inline-flex h-11 items-center gap-2 rounded-lg bg-primary px-5 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
              >
                Start Health Assessment
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <a
                href="#how-it-works"
                className="inline-flex h-11 items-center rounded-lg border border-border bg-background px-5 text-sm font-medium text-foreground hover:bg-muted transition-colors"
              >
                See How It Works
              </a>
            </motion.div>

            {/* Trust metrics */}
            <motion.div
              variants={fadeUp}
              className="flex flex-wrap items-center gap-6 justify-center lg:justify-start pt-2"
            >
              {[
                { value: "4", label: "Specialized AI Agents" },
                { value: "HITL", label: "Physician Review Loop" },
                { value: "CMAR", label: "Reasoning Architecture" },
              ].map((m) => (
                <div key={m.label} className="flex flex-col items-center lg:items-start gap-0.5">
                  <span className="text-lg font-bold tracking-tight">{m.value}</span>
                  <span className="text-[11px] text-muted-foreground">{m.label}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* Orb */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="hidden lg:block"
          >
            <HeroOrb />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
