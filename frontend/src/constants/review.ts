export const REVIEW_STATUS_LABELS: Record<string, string> = {
  NEW: "New",
  ASSIGNED: "Assigned",
  UNDER_REVIEW: "Under Review",
  APPROVED: "Approved",
  REJECTED: "Rejected",
  OVERRIDDEN: "Overridden",
  CLOSED: "Closed",
};

export const REVIEW_STATUS_COLORS: Record<string, string> = {
  NEW: "bg-info/10 text-info",
  ASSIGNED: "bg-warning/10 text-warning",
  UNDER_REVIEW: "bg-warning/10 text-warning",
  APPROVED: "bg-success/10 text-success",
  REJECTED: "bg-error/10 text-error",
  OVERRIDDEN: "bg-primary/10 text-primary",
  CLOSED: "bg-muted text-muted-foreground",
};
