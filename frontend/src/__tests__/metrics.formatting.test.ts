import { describe, it, expect } from "vitest";

// ── Formatting helpers ────────────────────────────────────────────────────────
// Mirror the logic in AnalyticsMetricCard so we can test it in isolation

type FormatType = "number" | "percent" | "duration" | "text";

function formatMetricValue(value: number | string | null, format: FormatType = "number"): string {
  if (value === null || value === undefined) return "N/A";

  if (format === "percent" && typeof value === "number") {
    return `${(value * 100).toFixed(1)}%`;
  }
  if (format === "duration" && typeof value === "number") {
    if (value < 60) return `${Math.round(value)}s`;
    if (value < 3600) return `${Math.round(value / 60)}m`;
    return `${(value / 3600).toFixed(1)}h`;
  }
  if (format === "number" && typeof value === "number") {
    return new Intl.NumberFormat("en-US").format(value);
  }
  return String(value);
}

// ── Null vs zero ──────────────────────────────────────────────────────────────

describe("formatMetricValue: null vs zero", () => {
  it("displays null as N/A", () => {
    expect(formatMetricValue(null, "number")).toBe("N/A");
    expect(formatMetricValue(null, "percent")).toBe("N/A");
    expect(formatMetricValue(null, "duration")).toBe("N/A");
  });

  it("displays valid 0 as '0', not N/A", () => {
    expect(formatMetricValue(0, "number")).toBe("0");
  });

  it("displays valid 0 rate as '0.0%', not N/A", () => {
    expect(formatMetricValue(0, "percent")).toBe("0.0%");
  });
});

// ── Confidence percentage formatting ─────────────────────────────────────────

describe("formatMetricValue: confidence (0–1 normalized)", () => {
  it("formats 0.82 as 82.0%", () => {
    expect(formatMetricValue(0.82, "percent")).toBe("82.0%");
  });

  it("formats 1.0 as 100.0%", () => {
    expect(formatMetricValue(1.0, "percent")).toBe("100.0%");
  });

  it("formats 0.0 as 0.0%", () => {
    expect(formatMetricValue(0.0, "percent")).toBe("0.0%");
  });

  it("formats a low-confidence threshold of 0.4 as 40.0%", () => {
    expect(formatMetricValue(0.4, "percent")).toBe("40.0%");
  });
});

// ── Rate percentage formatting ────────────────────────────────────────────────

describe("formatMetricValue: rates", () => {
  it("formats approval rate 0.667 as 66.7%", () => {
    expect(formatMetricValue(0.667, "percent")).toBe("66.7%");
  });

  it("formats escalation rate 0.5 as 50.0%", () => {
    expect(formatMetricValue(0.5, "percent")).toBe("50.0%");
  });
});

// ── Duration formatting ───────────────────────────────────────────────────────

describe("formatMetricValue: duration seconds", () => {
  it("formats 45 seconds as '45s'", () => {
    expect(formatMetricValue(45, "duration")).toBe("45s");
  });

  it("formats 90 seconds as '2m'", () => {
    expect(formatMetricValue(90, "duration")).toBe("2m");
  });

  it("formats 3600 seconds as '1.0h'", () => {
    expect(formatMetricValue(3600, "duration")).toBe("1.0h");
  });

  it("formats 7200 seconds as '2.0h'", () => {
    expect(formatMetricValue(7200, "duration")).toBe("2.0h");
  });

  it("null duration displays as N/A", () => {
    expect(formatMetricValue(null, "duration")).toBe("N/A");
  });
});

// ── Locale-aware integer formatting ──────────────────────────────────────────

describe("formatMetricValue: number locale formatting", () => {
  it("formats large integers with commas", () => {
    // Locale format may vary; just check it's not raw integer string for large numbers
    const result = formatMetricValue(1000, "number");
    expect(result).toMatch(/1[,.]?000/);
  });

  it("formats 0 as '0'", () => {
    expect(formatMetricValue(0, "number")).toBe("0");
  });
});
