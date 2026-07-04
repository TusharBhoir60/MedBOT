"use client";

import { motion } from "framer-motion";

const DOT_VARIANTS = {
  animate: (i: number) => ({
    y: [0, -6, 0],
    transition: {
      duration: 0.8,
      delay: i * 0.15,
      repeat: Infinity,
      ease: "easeInOut",
    },
  }),
};

export function TypingIndicator() {
  return (
    <div className="flex items-end gap-3 px-1">
      {/* Avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary ring-1 ring-primary/30">
        <span className="text-xs font-semibold">AI</span>
      </div>

      {/* Bubble */}
      <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-sm border border-border/50 bg-card/60 px-4 py-3 backdrop-blur-sm">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            custom={i}
            variants={DOT_VARIANTS}
            animate="animate"
            className="h-2 w-2 rounded-full bg-primary/60"
          />
        ))}
      </div>
    </div>
  );
}
