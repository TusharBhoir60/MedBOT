"use client";

import { motion } from "framer-motion";
import { format } from "date-fns";
import { Copy, Check } from "lucide-react";
import { useState, memo } from "react";
import { cn } from "@/lib/utils";
import { LocalMessage } from "@/hooks/use-chat";

interface MessageBubbleProps {
  message: LocalMessage;
  userInitial?: string;
}

export const MessageBubble = memo(function MessageBubble({
  message,
  userInitial = "U",
}: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isHuman = message.role === "human";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={cn(
        "group flex items-end gap-3",
        isHuman && "flex-row-reverse"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
          isHuman
            ? "bg-primary text-primary-foreground"
            : "bg-primary/20 text-primary ring-1 ring-primary/30"
        )}
        aria-hidden="true"
      >
        {isHuman ? userInitial : "AI"}
      </div>

      {/* Content */}
      <div className={cn("flex max-w-[75%] flex-col gap-1", isHuman && "items-end")}>
        <div
          className={cn(
            "relative rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isHuman
              ? "rounded-br-sm bg-primary text-primary-foreground"
              : "rounded-bl-sm border border-border/50 bg-card/60 text-foreground backdrop-blur-sm"
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>

          {/* Copy button */}
          <button
            onClick={handleCopy}
            className={cn(
              "absolute -top-2 right-2 flex h-6 w-6 items-center justify-center rounded-full border border-border/50 bg-background/80 opacity-0 shadow-sm transition-all group-hover:opacity-100",
              isHuman ? "-left-2 right-auto" : ""
            )}
            aria-label="Copy message"
          >
            {copied ? (
              <Check className="h-3 w-3 text-emerald-400" />
            ) : (
              <Copy className="h-3 w-3 text-muted-foreground" />
            )}
          </button>
        </div>

        {/* Timestamp */}
        <p className="text-xs text-muted-foreground/60">
          {format(message.timestamp, "HH:mm")}
        </p>
      </div>
    </motion.div>
  );
});
