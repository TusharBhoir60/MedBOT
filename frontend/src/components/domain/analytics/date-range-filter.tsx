"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useState } from "react";
import { subDays, startOfDay, endOfDay } from "date-fns";
import { Button } from "@/components/ui/button";
import { CalendarDays } from "lucide-react";

type Preset = "all" | "7d" | "30d";

export function DateRangeFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Determine active preset based on URL
  const getActivePreset = (): Preset => {
    const start = searchParams.get("startDate");
    const end = searchParams.get("endDate");
    if (!start && !end) return "all";
    // We could parse the dates, but for simplicity, we just manage local state
    // and sync back. In a real app we'd verify the exact diff.
    return "all"; // We'll rely on local state for the active button highlighting if needed
  };

  const [active, setActive] = useState<Preset>(getActivePreset());

  const applyRange = useCallback(
    (preset: Preset) => {
      setActive(preset);
      const params = new URLSearchParams(searchParams.toString());

      if (preset === "all") {
        params.delete("startDate");
        params.delete("endDate");
      } else {
        const today = new Date();
        let start = new Date();
        if (preset === "7d") start = subDays(today, 7);
        if (preset === "30d") start = subDays(today, 30);

        // Normalize to UTC strings using start/end of day
        // Since we want to pass standard ISO strings
        params.set("startDate", startOfDay(start).toISOString());
        params.set("endDate", endOfDay(today).toISOString());
      }

      router.push(`${pathname}?${params.toString()}`);
    },
    [pathname, router, searchParams]
  );

  return (
    <div className="flex items-center gap-2">
      <CalendarDays className="h-4 w-4 text-muted-foreground mr-1" />
      <span className="text-sm font-medium text-muted-foreground">Filter:</span>
      <div className="flex bg-secondary/50 rounded-md p-0.5 border border-border/50">
        <Button
          variant={active === "all" ? "default" : "ghost"}
          size="sm"
          className="h-7 text-xs px-3"
          onClick={() => applyRange("all")}
        >
          All Time
        </Button>
        <Button
          variant={active === "7d" ? "default" : "ghost"}
          size="sm"
          className="h-7 text-xs px-3"
          onClick={() => applyRange("7d")}
        >
          Last 7 Days
        </Button>
        <Button
          variant={active === "30d" ? "default" : "ghost"}
          size="sm"
          className="h-7 text-xs px-3"
          onClick={() => applyRange("30d")}
        >
          Last 30 Days
        </Button>
      </div>
    </div>
  );
}
