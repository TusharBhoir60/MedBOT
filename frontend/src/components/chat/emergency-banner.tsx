"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Phone } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmergencyBannerProps {
  visible: boolean;
  className?: string;
}

export function EmergencyBanner({ visible, className }: EmergencyBannerProps) {
  if (!visible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex items-start gap-3 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-300",
        className
      )}
      role="alert"
      aria-live="assertive"
    >
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
      <div className="flex-1 space-y-1">
        <p className="text-sm font-semibold text-red-200">Urgent medical attention required</p>
        <p className="text-xs leading-relaxed opacity-80">
          Based on your symptoms, this may require immediate care. Please call emergency services or
          go to the nearest emergency room now.
        </p>
      </div>
      <a
        href="tel:102"
        className="flex items-center gap-1.5 rounded-lg bg-red-500 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-red-400"
        aria-label="Call emergency services"
      >
        <Phone className="h-3.5 w-3.5" />
        102
      </a>
    </motion.div>
  );
}
