"use client";

import { useEffect, useRef } from "react";
import { AnimatePresence } from "framer-motion";
import { Bot, Sparkles } from "lucide-react";
import { LocalMessage } from "@/hooks/use-chat";
import { MessageBubble } from "@/components/chat/message-bubble";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import { EmergencyBanner } from "@/components/chat/emergency-banner";
import { MedicalDisclaimer } from "@/components/chat/medical-disclaimer";
import { ChatResponse } from "@/schemas/chat.schema";

interface ChatWindowProps {
  messages: LocalMessage[];
  isLoading: boolean;
  latestResponse: ChatResponse | null;
  userInitial?: string;
}

const WELCOME_PROMPTS = [
  "I've been having chest pain for 2 days",
  "My child has a fever of 102°F",
  "I have a severe headache and sensitivity to light",
  "I've noticed unusual fatigue and shortness of breath",
];

function EmptyState({ onPromptClick }: { onPromptClick: (prompt: string) => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-8 px-4 py-10 text-center">
      <div className="space-y-3">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/20">
          <Bot className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold tracking-tight">AarogyaAgent AI</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            I&apos;ll guide you through a structured clinical assessment.
          </p>
        </div>
      </div>

      {/* Starter prompts */}
      <div className="grid w-full max-w-md gap-2">
        {WELCOME_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onPromptClick(prompt)}
            className="group flex items-center gap-3 rounded-xl border border-border/50 bg-card/40 px-4 py-3 text-left text-sm text-muted-foreground transition-all hover:border-primary/30 hover:bg-primary/5 hover:text-foreground"
          >
            <Sparkles className="h-3.5 w-3.5 shrink-0 text-primary/60 group-hover:text-primary" />
            {prompt}
          </button>
        ))}
      </div>

      <MedicalDisclaimer compact className="max-w-md" />
    </div>
  );
}

export function ChatWindow({ messages, isLoading, latestResponse, userInitial }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const isEscalated = latestResponse?.escalation_decision ?? false;

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex h-full flex-col">
      {/* Emergency banner */}
      <AnimatePresence>
        {isEscalated && (
          <EmergencyBanner visible className="m-4 mb-0" />
        )}
      </AnimatePresence>

      {/* Messages area */}
      <div className="flex flex-1 flex-col overflow-y-auto px-4 py-4 scrollbar-thin scrollbar-thumb-border">
        {messages.length === 0 ? (
          <EmptyState onPromptClick={() => {}} />
        ) : (
          <div className="flex flex-col gap-5">
            <AnimatePresence initial={false}>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} userInitial={userInitial} />
              ))}
            </AnimatePresence>

            {/* Typing indicator */}
            <AnimatePresence>
              {isLoading && <TypingIndicator key="typing" />}
            </AnimatePresence>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
