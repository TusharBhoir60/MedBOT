"use client";

import { motion } from "framer-motion";
import { ArrowDown, TrendingUp } from "lucide-react";
import { staggerContainer, fadeUp } from "@/components/ui/motion";

const agents = [
  { name: "Intake Agent", desc: "Extracts demographics, chief complaint, and symptom onset.", color: "border-info/30 bg-info/5" },
  { name: "Symptom Agent", desc: "Standardizes symptoms and maps to clinical categories.", color: "border-primary/30 bg-primary/5" },
  { name: "Diagnosis Agent", desc: "RAG-powered differential diagnosis with literature citations.", color: "border-warning/30 bg-warning/5" },
  { name: "Follow-up Agent", desc: "Generates clarifying questions when uncertainty is detected.", color: "border-success/30 bg-success/5" },
];

const outcomes = [
  { label: "Confidence ≥ 85%", desc: "Response delivered automatically", color: "bg-success/10 text-success border-success/20" },
  { label: "Confidence 60–84%", desc: "Flagged for physician spot-check", color: "bg-warning/10 text-warning border-warning/20" },
  { label: "Confidence < 60%", desc: "Mandatory physician review before delivery", color: "bg-error/10 text-error border-error/20" },
];

export function CMARSection() {
  return (
    <section id="cmar" className="py-24 sm:py-32 bg-muted/30">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="flex flex-col items-center gap-4 text-center mb-16"
        >
          <motion.p variants={fadeUp} className="text-xs font-medium uppercase tracking-widest text-primary">
            Architecture
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl font-bold tracking-tight sm:text-4xl">
            Confidence-Weighted Multi-Agent Reasoning
          </motion.h2>
          <motion.p variants={fadeUp} className="max-w-xl text-muted-foreground text-base">
            CMAR is the reasoning framework that makes AarogyaAgent fundamentally different from general-purpose LLMs.
            Each agent is purpose-built, sequentially composed, and independently validated.
          </motion.p>
        </motion.div>

        <div className="grid gap-10 lg:grid-cols-2 lg:gap-16 items-start">
          {/* Agent Pipeline */}
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-6 uppercase tracking-wider">Agent Pipeline</p>
            <div className="flex flex-col gap-0">
              {agents.map((agent, i) => (
                <div key={agent.name} className="flex flex-col">
                  <motion.div
                    initial={{ opacity: 0, x: -16 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.45, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                    className={`rounded-lg border p-4 ${agent.color} transition-shadow hover:shadow-sm`}
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{agent.name}</p>
                      <span className="text-[10px] text-muted-foreground font-mono bg-muted rounded px-1.5 py-0.5">
                        agent_{i + 1}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{agent.desc}</p>
                  </motion.div>
                  {i < agents.length - 1 && (
                    <div className="flex h-7 w-full items-center justify-center text-muted-foreground/30">
                      <ArrowDown className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Confidence routing */}
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-6 uppercase tracking-wider">Confidence Routing</p>
            <div className="mb-6 rounded-lg border border-border bg-card p-5">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="h-5 w-5 text-primary" />
                <p className="text-sm font-semibold">Confidence Score Output</p>
              </div>
              <div className="h-3 w-full rounded-full bg-gradient-to-r from-error via-warning to-success overflow-hidden">
                <motion.div
                  className="h-full w-full"
                  initial={{ scaleX: 0 }}
                  whileInView={{ scaleX: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
                  style={{ transformOrigin: "left" }}
                />
              </div>
              <div className="mt-1.5 flex justify-between text-[10px] text-muted-foreground">
                <span>0%</span>
                <span>60%</span>
                <span>85%</span>
                <span>100%</span>
              </div>
            </div>

            <div className="flex flex-col gap-3">
              {outcomes.map((o, i) => (
                <motion.div
                  key={o.label}
                  initial={{ opacity: 0, x: 16 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.45, delay: i * 0.1 + 0.2, ease: [0.22, 1, 0.36, 1] }}
                  className={`flex items-center gap-3 rounded-lg border px-4 py-3 ${o.color}`}
                >
                  <span className="h-2 w-2 rounded-full bg-current shrink-0" />
                  <div>
                    <p className="text-xs font-semibold">{o.label}</p>
                    <p className="text-[11px] opacity-75 mt-0.5">{o.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
