import { useState, useRef, useEffect } from "react";
import { ReviewTaskResponse } from "@/schemas/review.schema";
import { useReviewActions } from "@/hooks/use-review";
import { MessageSquare, Send, User } from "lucide-react";
import { cn } from "@/lib/utils";

export function CommentPanel({ task }: { task: ReviewTaskResponse }) {
  const [content, setContent] = useState("");
  const { addComment } = useReviewActions(task.id);
  const endRef = useRef<HTMLDivElement>(null);

  const isSubmitting = addComment.isPending;
  const comments = task.comments || [];

  const handleSend = () => {
    if (!content.trim() || isSubmitting) return;
    addComment.mutate({ content: content.trim() });
    setContent("");
  };

  useEffect(() => {
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [comments.length]);

  return (
    <div className="flex h-full flex-col rounded-xl border border-border/50 bg-card shadow-sm">
      <div className="flex items-center gap-2 border-b border-border/50 p-4">
        <MessageSquare className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold tracking-tight">Review Discussion</h3>
      </div>
      
      {/* Comments List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-border">
        {comments.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center text-muted-foreground">
            <MessageSquare className="mb-2 h-8 w-8 opacity-20" />
            <p className="text-xs">No comments yet. Start the discussion.</p>
          </div>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="flex gap-3">
              <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <User className="h-3 w-3" />
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium">{comment.author_id || "System"}</span>
                  <span className="text-[10px] text-muted-foreground">Just now</span>
                </div>
                <div className="rounded-xl rounded-tl-sm bg-muted/40 p-2.5 text-sm text-card-foreground/90">
                  {comment.content}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border/50 bg-background/50 p-3">
        <div className="relative flex items-end gap-2">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Add a comment..."
            className="max-h-32 min-h-[40px] w-full resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 scrollbar-thin scrollbar-thumb-border"
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!content.trim() || isSubmitting}
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-md transition-colors",
              content.trim() && !isSubmitting ? "bg-primary text-primary-foreground hover:bg-primary/90" : "bg-muted text-muted-foreground cursor-not-allowed"
            )}
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
