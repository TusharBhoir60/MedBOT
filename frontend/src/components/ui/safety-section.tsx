"use client";

import { motion } from "framer-motion";
import { ShieldCheck, UserRound, Lock, Server } from "lucide-react";
import { staggerContainer, fadeUp } from "@/components/ui/motion";

const pillars = [
  {
    icon: UserRound,
    title: "AI assists. Physicians decide.",
    description:
      "AarogyaAgent is a decision-support tool, not a replacement for clinical judgment. All high-stakes outputs require physician sign-off before delivery.",
  },
  {
    icon: ShieldCheck,
    title: "Human review, always available",
    description:
      "No case is processed without the possibility of physician review. Complex or low-confidence cases are automatically escalated via the HITL queue.",
  },
  {
    icon: Lock,
    title: "Privacy-first architecture",
    description:
      "Session data is isolated per-patient. JWT authentication and role-based access control enforce data boundaries across all roles.",
  },
  {
    icon: Server,
    title: "Auditable infrastructure",
    description:
      "Every agent step, confidence score, and physician override is logged with a correlation ID for full auditability and regulatory compliance.",
  },
];

export function SafetySection() {
  return (
    <section id="safety" className="py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="flex flex-col items-center gap-4 text-center mb-16"
        >
          <motion.p variants={fadeUp} className="text-xs font-medium uppercase tracking-widest text-primary">
            Safety &amp; Trust
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl font-bold tracking-tight sm:text-4xl">
            Designed for clinical accountability
          </motion.h2>
          <motion.p variants={fadeUp} className="max-w-xl text-muted-foreground text-base">
            Every architectural decision in AarogyaAgent reflects a single principle: AI should augment, never
            circumvent, clinical judgment.
          </motion.p>
        </motion.div>

        <div className="grid gap-6 sm:grid-cols-2">
          {pillars.map((p, i) => (
            <motion.div
              key={p.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.45, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
              className="flex gap-4 rounded-xl border border-border bg-card p-6 hover:shadow-sm transition-shadow"
            >
              <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <p.icon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-sm font-semibold mb-1.5">{p.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{p.description}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Disclaimer banner */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-10 rounded-lg border border-warning/20 bg-warning/5 px-5 py-4 text-xs text-warning-foreground/80 text-center"
        >
          <strong>Medical Disclaimer:</strong> AarogyaAgent is an AI-assisted triage tool. It does not provide medical
          diagnoses and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a
          qualified healthcare provider with questions regarding medical conditions.
        </motion.div>
      </div>
    </section>
  );
}
