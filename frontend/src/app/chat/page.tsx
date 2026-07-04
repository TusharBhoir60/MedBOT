"use client";

import { useState } from "react";
import { PatientLayout } from "@/components/layout/patient-layout";
import { useChat } from "@/hooks/use-chat";
import { useAuth } from "@/providers/auth-provider";
import { ChatWindow } from "@/components/chat/chat-window";
import { ChatInput } from "@/components/chat/chat-input";
import { ConversationSidebar } from "@/components/chat/conversation-sidebar";
import { InformationPanel } from "@/components/chat/information-panel";
import { ConversationSummary } from "@/services/chat.service";
import { PanelRight, PanelLeft, X } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ChatPage() {
  const { user } = useAuth();
  const { messages, isLoading, latestResponse, error, sendMessage, startNewChat, loadSession, sessionId } = useChat();

  const [inputValue, setInputValue] = useState("");
  const [showInfoPanel, setShowInfoPanel] = useState(true);
  const [showSidebar, setShowSidebar] = useState(false); // mobile

  const userInitial = user?.sub?.[0]?.toUpperCase() ?? "U";

  const handleSelectSession = async (session: ConversationSummary) => {
    await loadSession(session);
    setShowSidebar(false);
  };

  return (
    <PatientLayout>
      <div className="flex h-full overflow-hidden">
        {/* ── Left: Conversation Sidebar (desktop always, mobile as drawer) ── */}
        <div className="hidden w-64 shrink-0 xl:block">
          <ConversationSidebar
            activeSessionId={sessionId}
            onNewChat={startNewChat}
            onSelectSession={handleSelectSession}
            className="h-full"
          />
        </div>

        {/* Mobile sidebar drawer */}
        {showSidebar && (
          <div
            className="fixed inset-0 z-50 xl:hidden"
            onClick={() => setShowSidebar(false)}
          >
            <div className="absolute inset-0 bg-black/50" />
            <div
              className="absolute inset-y-0 left-0 w-72 animate-in slide-in-from-left-full"
              onClick={(e) => e.stopPropagation()}
            >
              <ConversationSidebar
                activeSessionId={sessionId}
                onNewChat={() => { startNewChat(); setShowSidebar(false); }}
                onSelectSession={handleSelectSession}
                className="h-full"
              />
            </div>
          </div>
        )}

        {/* ── Center: Chat Area ─────────────────────────────────────────── */}
        <div className="flex min-w-0 flex-1 flex-col">
          {/* Top toolbar */}
          <div className="flex items-center justify-between border-b border-border/40 px-4 py-2.5">
            <button
              onClick={() => setShowSidebar(true)}
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition hover:bg-muted xl:hidden"
              aria-label="Open conversation history"
            >
              <PanelLeft className="h-4 w-4" />
            </button>
            <span className="text-sm font-medium text-muted-foreground">Health Assessment</span>
            <button
              onClick={() => setShowInfoPanel((v) => !v)}
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition hover:bg-muted",
                showInfoPanel && "bg-primary/10 text-primary"
              )}
              aria-label={showInfoPanel ? "Hide info panel" : "Show info panel"}
            >
              <PanelRight className="h-4 w-4" />
            </button>
          </div>

          {/* Chat window */}
          <div className="flex-1 overflow-hidden">
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              latestResponse={latestResponse}
              userInitial={userInitial}
            />
          </div>

          {/* Error banner */}
          {error && (
            <div className="mx-4 mb-2 flex items-center gap-2 rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-300 ring-1 ring-red-500/20">
              <span className="flex-1">{error}</span>
              <button onClick={() => {}} aria-label="Dismiss">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Input area */}
          <div className="border-t border-border/40 bg-background/60 px-4 py-4 backdrop-blur-sm">
            <ChatInput
              value={inputValue}
              onChange={setInputValue}
              onSend={(msg) => {
                sendMessage(msg);
                setInputValue("");
              }}
              onClear={() => setInputValue("")}
              isLoading={isLoading}
            />
            <p className="mt-2 text-center text-xs text-muted-foreground/50">
              Enter to send · Shift+Enter for new line
            </p>
          </div>
        </div>

        {/* ── Right: Information Panel ──────────────────────────────────── */}
        {showInfoPanel && (
          <div className="hidden w-72 shrink-0 border-l border-border/40 lg:block">
            <InformationPanel
              response={latestResponse}
              isLoading={isLoading}
              className="h-full"
            />
          </div>
        )}
      </div>
    </PatientLayout>
  );
}
