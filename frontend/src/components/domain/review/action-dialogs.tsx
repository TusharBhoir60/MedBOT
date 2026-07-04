import { useState, useEffect } from "react";
import { ReviewTaskResponse } from "@/schemas/review.schema";
import { useReviewActions } from "@/hooks/use-review";
import { X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ActionDialogsProps {
  task: ReviewTaskResponse;
  rejectOpen: boolean;
  onRejectClose: () => void;
  overrideOpen: boolean;
  onOverrideClose: () => void;
}

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}

function Dialog({ isOpen, onClose, title, children, footer }: DialogProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] rounded-xl border border-border bg-card shadow-lg"
          >
            <div className="flex items-center justify-between border-b border-border p-4">
              <h2 className="text-lg font-semibold">{title}</h2>
              <button onClick={onClose} className="rounded-md p-1 hover:bg-muted"><X className="h-4 w-4" /></button>
            </div>
            <div className="p-4">{children}</div>
            <div className="flex items-center justify-end gap-2 border-t border-border p-4 bg-muted/20">
              {footer}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export function ActionDialogs({ task, rejectOpen, onRejectClose, overrideOpen, onOverrideClose }: ActionDialogsProps) {
  const { rejectTask, overrideTask } = useReviewActions(task.id);
  const [rejectReason, setRejectReason] = useState("");
  const [overrideData, setOverrideData] = useState("");

  useEffect(() => {
    let mounted = true;
    if (overrideOpen && mounted) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setOverrideData(JSON.stringify(task.final_response || task.diagnosis_output || {}, null, 2));
    }
    return () => { mounted = false; };
  }, [overrideOpen, task]);

  const handleReject = () => {
    rejectTask.mutate({ reason: rejectReason });
    setRejectReason("");
    onRejectClose();
  };

  const handleOverride = () => {
    try {
      const parsed = JSON.parse(overrideData);
      overrideTask.mutate({ final_response: parsed });
      onOverrideClose();
    } catch {
      alert("Invalid JSON format. Please correct it before saving.");
    }
  };



  return (
    <>
      <Dialog
        isOpen={rejectOpen}
        onClose={onRejectClose}
        title="Reject Assessment"
        footer={
          <>
            <button onClick={onRejectClose} className="rounded-md px-4 py-2 text-sm font-medium hover:bg-muted">Cancel</button>
            <button
              onClick={handleReject}
              disabled={rejectTask.isPending}
              className="rounded-md bg-red-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-600 disabled:opacity-50"
            >
              Confirm Rejection
            </button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Please provide a reason for rejecting this AI assessment. This helps improve the system.</p>
          <textarea
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Reason for rejection..."
            className="min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>
      </Dialog>

      <Dialog
        isOpen={overrideOpen}
        onClose={onOverrideClose}
        title="Override AI Assessment"
        footer={
          <>
            <button onClick={onOverrideClose} className="rounded-md px-4 py-2 text-sm font-medium hover:bg-muted">Cancel</button>
            <button
              onClick={handleOverride}
              disabled={overrideTask.isPending}
              className="rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-amber-600 disabled:opacity-50"
            >
              Save Override
            </button>
          </>
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Modify the final response payload directly.</p>
          <textarea
            value={overrideData}
            onChange={(e) => setOverrideData(e.target.value)}
            className="min-h-[250px] w-full rounded-md border border-input bg-muted/50 px-3 py-2 font-mono text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>
      </Dialog>
    </>
  );
}
