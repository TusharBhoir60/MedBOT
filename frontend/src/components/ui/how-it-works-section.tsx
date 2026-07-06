"use client";

import { motion } from "framer-motion";
import { UserRound, Brain, Stethoscope, MessageSquare, ArrowDown } from "lucide-react";
import { staggerContainer, fadeUp } from "@/components/ui/motion";

const steps = [
  {
    icon: UserRound,
    title: "Patient Describes Symptoms",
    description: "The patient enters their chief complaint and any relevant history. No sign-up required to begin.",
    color: "bg-info/10 text-info border-info/20",
  },
  {
    icon: Brain,
    title: "Multi-Agent AI Analysis",
    description: "Four specialized AI agents — Intake, Symptom, Diagnosis, and Follow-up — reason through the case in a structured pipeline.",
    color: "bg-primary/10 text-primary border-primary/20",
  },
  {
    icon: Stethoscope,
    title: "Physician Review (If Required)",
    description: "If confidence is below threshold or the case is flagged as complex, it's automatically escalated to a licensed physician.",
    color: "bg-warning/10 text-warning border-warning/20",
  },
  {
    icon: MessageSquare,
    title: "Personalized Recommendation",
    description: "A clear, evidence-backed response — reviewed or approved by a physician — is delivered to the patient.",
    color: "bg-success/10 text-success border-success/20",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="flex flex-col items-center gap-4 text-center mb-16"
        >
          <motion.p variants={fadeUp} className="text-xs font-medium uppercase tracking-widest text-primary">
            Workflow
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-3xl font-bold tracking-tight sm:text-4xl">
            From symptom to clarity — in seconds
          </motion.h2>
          <motion.p variants={fadeUp} className="max-w-xl text-muted-foreground text-base">
            AarogyaAgent&apos;s structured pipeline ensures every case receives systematic, evidence-weighted analysis before
            a response reaches the patient.
          </motion.p>
        </motion.div>

        {/* Steps */}
        <div className="relative flex flex-col items-center gap-0">
          {steps.map((step, i) => (
            <div key={step.title} className="flex flex-col items-center w-full max-w-lg">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.5, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                className={`w-full rounded-xl border p-5 bg-card flex items-start gap-4 ${step.color.replace("text-", "border-").split(" ")[0]} hover:shadow-sm transition-shadow`}
              >
                <div className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border ${step.color}`}>
                  <step.icon className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-muted-foreground">Step {i + 1}</span>
                  </div>
                  <h3 className="text-sm font-semibold mb-1">{step.title}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed">{step.description}</p>
                </div>
              </motion.div>
              {i < steps.length - 1 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 + 0.3 }}
                  className="flex h-10 items-center justify-center text-muted-foreground/40"
                >
                  <ArrowDown className="h-5 w-5" />
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
