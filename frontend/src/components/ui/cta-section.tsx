"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Activity } from "lucide-react";
import { ROUTES } from "@/constants/routes";
import { fadeUp } from "@/components/ui/motion";

export function CTASection() {
  return (
    <section className="py-24 sm:py-32">
      <div className="mx-auto max-w-4xl px-4 sm:px-6">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          variants={fadeUp}
          className="relative overflow-hidden rounded-2xl border border-primary/20 bg-primary/5 px-6 py-16 text-center sm:px-16 sm:py-20"
        >
          {/* Background glow */}
          <div
            className="absolute left-1/2 top-1/2 -z-10 h-[200px] w-[200px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/20 blur-3xl"
            aria-hidden="true"
          />

          <div className="mx-auto mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Activity className="h-6 w-6 text-primary" />
          </div>

          <h2 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight sm:text-4xl">
            Experience the future of clinical triage.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-base text-muted-foreground">
            No signup required to try the patient interface. Start a session now to see the multi-agent reasoning
            engine in action.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              href={ROUTES.chat}
              className="group inline-flex h-11 items-center gap-2 rounded-lg bg-primary px-6 text-sm font-medium text-primary-foreground hover:opacity-90 transition-opacity"
            >
              Start Assessment
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href={ROUTES.login}
              className="inline-flex h-11 items-center rounded-lg border border-border bg-background px-6 text-sm font-medium text-foreground hover:bg-muted transition-colors"
            >
              Physician Login
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
