"use client";

import { useCallback, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Send, Mic, Paperclip, X } from "lucide-react";
import { cn } from "@/lib/utils";

const MAX_CHARS = 2000;

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  value: string;
  onChange: (value: string) => void;
  onClear?: () => void;
  className?: string;
}

export function ChatInput({
  onSend,
  isLoading,
  value,
  onChange,
  onClear,
  className,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-expand textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    onChange("");
  }, [value, isLoading, onSend, onChange]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const remaining = MAX_CHARS - value.length;
  const isOverLimit = remaining < 0;
  const isNearLimit = remaining < 100;

  return (
    <div
      className={cn(
        "relative rounded-2xl border border-border/60 bg-card/60 shadow-lg backdrop-blur-sm transition-all",
        "focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20",
        className
      )}
    >
      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Describe your symptoms… (Enter to send, Shift+Enter for new line)"
        disabled={isLoading}
        aria-label="Message input"
        aria-multiline="true"
        rows={1}
        maxLength={MAX_CHARS}
        className={cn(
          "w-full resize-none bg-transparent px-4 py-3.5 pr-20 text-sm placeholder-muted-foreground/50",
          "focus:outline-none disabled:opacity-50",
          "max-h-40 min-h-[52px]"
        )}
      />

      {/* Toolbar row */}
      <div className="flex items-center justify-between px-3 pb-2.5 pt-0">
        <div className="flex items-center gap-1">
          {/* Attachment placeholder */}
          <button
            type="button"
            disabled
            aria-label="Attach file (coming soon)"
            title="Attachments coming soon"
            className="flex h-7 w-7 items-center justify-center rounded-lg text-muted-foreground/40 disabled:cursor-not-allowed"
          >
            <Paperclip className="h-4 w-4" />
          </button>

          {/* Voice placeholder */}
          <button
            type="button"
            disabled
            aria-label="Voice input (coming soon)"
            title="Voice input coming soon"
            className="flex h-7 w-7 items-center justify-center rounded-lg text-muted-foreground/40 disabled:cursor-not-allowed"
          >
            <Mic className="h-4 w-4" />
          </button>

          {/* Clear */}
          {value && onClear && (
            <button
              type="button"
              onClick={onClear}
              aria-label="Clear input"
              className="flex h-7 w-7 items-center justify-center rounded-lg text-muted-foreground/60 transition hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Character counter */}
          {isNearLimit && (
            <span className={cn("text-xs tabular-nums", isOverLimit ? "text-red-400" : "text-muted-foreground/60")}>
              {remaining}
            </span>
          )}

          {/* Send button */}
          <motion.button
            type="button"
            onClick={handleSend}
            disabled={isLoading || !value.trim() || isOverLimit}
            whileTap={{ scale: 0.92 }}
            aria-label="Send message"
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-xl transition-all",
              value.trim() && !isLoading && !isOverLimit
                ? "bg-primary text-primary-foreground shadow-md hover:bg-primary/90"
                : "bg-muted text-muted-foreground/40 cursor-not-allowed"
            )}
          >
            <Send className="h-4 w-4" />
          </motion.button>
        </div>
      </div>
    </div>
  );
}
