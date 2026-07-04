"use client";

import { motion } from "framer-motion";
import { X, Check } from "lucide-react";
import { staggerContainer, fadeUp } from "@/components/ui/motion";

const traditional = [
  "Single LLM with no confidence scoring",
  "No physician oversight mechanism",
  "Opaque reasoning — black-box outputs",
  "No structured differential diagnosis",
  "Generic responses without citation",
  "No escalation when uncertain",
];

const aarogya = [
  "CMAR: 4-agent pipeline with confidence scoring",
  "Human-in-the-loop physician review",
  "Transparent reasoning at each agent step",
  "Structured differential diagnosis output",
  "Evidence-grounded responses with citations",
  "Auto-escalates complex or low-confidence cases",
];

export function WhySection() {
  return (
    <section className="py-24 sm:py-32 bg-muted/30">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="flex flex-col items-center gap-4 text-center mb-16"
        >
          <motion.p variants={fadeUp} className="text-xs font-medium uppercase tracking-widest text-primary">
            Comparison
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl font-bold tracking-tight sm:text-4xl">
            Why AarogyaAgent?
          </motion.h2>
          <motion.p variants={fadeUp} className="max-w-xl text-muted-foreground text-base">
            General-purpose chatbots are not equipped for clinical reasoning. AarogyaAgent was built differently, from
            the ground up.
          </motion.p>
        </motion.div>

        <div className="grid gap-4 sm:grid-cols-2">
          {/* Traditional */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
            className="rounded-xl border border-border bg-card p-6"
          >
            <div className="flex items-center gap-2 mb-5">
              <div className="h-2.5 w-2.5 rounded-full bg-error" />
              <p className="text-sm font-semibold text-muted-foreground">Traditional Chatbots</p>
            </div>
            <ul className="flex flex-col gap-3">
              {traditional.map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <X className="mt-0.5 h-4 w-4 shrink-0 text-error" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>

          {/* AarogyaAgent */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
            className="rounded-xl border border-primary/30 bg-primary/5 p-6"
          >
            <div className="flex items-center gap-2 mb-5">
              <div className="h-2.5 w-2.5 rounded-full bg-success" />
              <p className="text-sm font-semibold">AarogyaAgent v2</p>
            </div>
            <ul className="flex flex-col gap-3">
              {aarogya.map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm">
                  <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
