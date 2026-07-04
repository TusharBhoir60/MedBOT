"use client";

import { motion } from "framer-motion";
import { Brain, ShieldCheck, BarChart2, BookOpen, Lock, Zap, Workflow, Stethoscope } from "lucide-react";
import { staggerContainer, fadeUp } from "@/components/ui/motion";

const features = [
  {
    icon: Brain,
    title: "AI Triage Engine",
    description: "A 4-agent pipeline independently analyzes each case, reducing single-model hallucination risk.",
  },
  {
    icon: Stethoscope,
    title: "Human-in-the-Loop",
    description: "Physicians can approve, override, or annotate any AI-generated response before it reaches the patient.",
  },
  {
    icon: BarChart2,
    title: "Confidence Scoring",
    description: "Every diagnosis comes with a quantified confidence score, not just a text response.",
  },
  {
    icon: BookOpen,
    title: "Evidence-backed",
    description: "The Diagnosis Agent uses RAG over a curated medical knowledge base to ground all claims.",
  },
  {
    icon: Lock,
    title: "Secure by Design",
    description: "JWT authentication, role-based access control, and request-level audit logging throughout.",
  },
  {
    icon: Zap,
    title: "Fast Assessment",
    description: "Most sessions complete the full multi-agent pipeline in under 10 seconds.",
  },
  {
    icon: Workflow,
    title: "Composable Pipeline",
    description: "Built on LangGraph — individual agents can be updated or swapped without rewriting the system.",
  },
  {
    icon: ShieldCheck,
    title: "Safety Validation",
    description: "All AI outputs pass through a response safety validator before being surfaced to users.",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="flex flex-col items-center gap-4 text-center mb-16"
        >
          <motion.p variants={fadeUp} className="text-xs font-medium uppercase tracking-widest text-primary">
            Capabilities
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl font-bold tracking-tight sm:text-4xl">
            Built for clinical reliability
          </motion.h2>
          <motion.p variants={fadeUp} className="max-w-xl text-muted-foreground text-base">
            Every design decision prioritizes accuracy, transparency, and physician trust over raw speed or scale.
          </motion.p>
        </motion.div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.45, delay: i * 0.06, ease: [0.22, 1, 0.36, 1] }}
              className="group flex flex-col gap-3 rounded-xl border border-border bg-card p-5 hover:shadow-sm hover:border-primary/20 transition-all"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary/15 transition-colors">
                <f.icon className="h-4.5 w-4.5 h-[18px] w-[18px]" />
              </div>
              <div>
                <h3 className="text-sm font-semibold mb-1">{f.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{f.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
