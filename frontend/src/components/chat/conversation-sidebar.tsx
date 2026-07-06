"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Search, MessageSquare, Trash2, Pencil, MoreHorizontal } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { chatService, ConversationSummary } from "@/services/chat.service";
import { cn } from "@/lib/utils";

interface ConversationSidebarProps {
  activeSessionId: string;
  onNewChat: () => void;
  onSelectSession: (session: ConversationSummary) => void;
  className?: string;
}

interface ConversationItemProps {
  session: ConversationSummary;
  isActive: boolean;
  onSelect: () => void;
  onDelete: (id: string) => void;
  onRename: (id: string, newTitle: string) => void;
}

function ConversationItem({ session, isActive, onSelect, onDelete, onRename }: ConversationItemProps) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(session.title ?? "Untitled");
  const [showMenu, setShowMenu] = useState(false);

  const submitRename = useCallback(() => {
    if (renameValue.trim() && renameValue !== session.title) {
      onRename(session.session_id, renameValue.trim());
    }
    setIsRenaming(false);
  }, [renameValue, session, onRename]);

  return (
    <div
      className={cn(
        "group relative flex cursor-pointer items-start gap-3 rounded-lg px-3 py-2.5 transition-all",
        isActive ? "bg-primary/10 ring-1 ring-primary/20" : "hover:bg-muted/40"
      )}
      onClick={onSelect}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onSelect()}
      aria-pressed={isActive}
    >
      <MessageSquare className={cn("mt-0.5 h-4 w-4 shrink-0", isActive ? "text-primary" : "text-muted-foreground/60")} />

      <div className="min-w-0 flex-1">
        {isRenaming ? (
          <input
            autoFocus
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onBlur={submitRename}
            onKeyDown={(e) => {
              if (e.key === "Enter") submitRename();
              if (e.key === "Escape") setIsRenaming(false);
            }}
            onClick={(e) => e.stopPropagation()}
            className="w-full rounded bg-background/60 px-1 text-sm text-foreground focus:outline-none"
          />
        ) : (
          <p className="truncate text-sm font-medium">{session.title ?? "Untitled"}</p>
        )}
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="text-xs text-muted-foreground/60 truncate">
            {session.last_message_preview ?? "No messages yet"}
          </span>
        </div>
        <p className="text-xs text-muted-foreground/40 mt-0.5">
          {formatDistanceToNow(new Date(session.updated_at), { addSuffix: true })}
        </p>
      </div>

      {/* Context menu */}
      <div className="relative shrink-0">
        <button
          onClick={(e) => { e.stopPropagation(); setShowMenu((v) => !v); }}
          className="flex h-6 w-6 items-center justify-center rounded opacity-0 transition group-hover:opacity-100 hover:bg-muted"
          aria-label="More options"
        >
          <MoreHorizontal className="h-3.5 w-3.5 text-muted-foreground" />
        </button>

        <AnimatePresence>
          {showMenu && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="absolute right-0 top-7 z-50 min-w-32 overflow-hidden rounded-lg border border-border/60 bg-popover shadow-lg"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs hover:bg-muted"
                onClick={() => { setIsRenaming(true); setShowMenu(false); }}
              >
                <Pencil className="h-3 w-3" /> Rename
              </button>
              <button
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs text-red-400 hover:bg-red-500/10"
                onClick={() => { onDelete(session.session_id); setShowMenu(false); }}
              >
                <Trash2 className="h-3 w-3" /> Delete
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export function ConversationSidebar({ activeSessionId, onNewChat, onSelectSession, className }: ConversationSidebarProps) {
  const [sessions, setSessions] = useState<ConversationSummary[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    chatService.getHistory().then((data) => {
      if (mounted) setSessions(data);
    }).catch(() => {/* ignore */}).finally(() => {
      if (mounted) setIsLoading(false);
    });
    return () => { mounted = false; };
  }, [activeSessionId]);

  const handleDelete = async (id: string) => {
    await chatService.deleteSession(id);
    setSessions((prev) => prev.filter((s) => s.session_id !== id));
    if (id === activeSessionId) onNewChat();
  };

  const handleRename = async (id: string, title: string) => {
    await chatService.renameSession(id, title);
    setSessions((prev) => prev.map((s) => s.session_id === id ? { ...s, title } : s));
  };

  const filtered = sessions.filter((s) =>
    (s.title ?? "").toLowerCase().includes(search.toLowerCase()) ||
    (s.last_message_preview ?? "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className={cn("flex h-full flex-col border-r border-border/50 bg-card/30 backdrop-blur-sm", className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/40">
        <span className="text-sm font-semibold">Conversations</span>
        <button
          onClick={onNewChat}
          className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary transition hover:bg-primary/20"
          aria-label="New conversation"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {/* Search */}
      <div className="px-3 py-2 border-b border-border/30">
        <div className="flex items-center gap-2 rounded-lg bg-muted/40 px-3 py-1.5">
          <Search className="h-3.5 w-3.5 shrink-0 text-muted-foreground/60" />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations…"
            className="w-full bg-transparent text-xs text-foreground placeholder-muted-foreground/50 focus:outline-none"
            aria-label="Search conversations"
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5 scrollbar-thin scrollbar-thumb-border">
        {isLoading && (
          <div className="px-3 py-4 text-center text-xs text-muted-foreground animate-pulse">Loading…</div>
        )}
        {!isLoading && filtered.length === 0 && (
          <div className="px-3 py-8 text-center">
            <MessageSquare className="mx-auto mb-2 h-6 w-6 text-muted-foreground/30" />
            <p className="text-xs text-muted-foreground/60">
              {search ? "No results found" : "Start a conversation to begin"}
            </p>
          </div>
        )}
        <AnimatePresence>
          {filtered.map((session) => (
            <motion.div
              key={session.session_id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.15 }}
            >
              <ConversationItem
                session={session}
                isActive={session.session_id === activeSessionId}
                onSelect={() => onSelectSession(session)}
                onDelete={handleDelete}
                onRename={handleRename}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
