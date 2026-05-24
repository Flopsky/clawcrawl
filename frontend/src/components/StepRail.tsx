"use client";

import { motion } from "framer-motion";
import { PIPELINE_STEPS, stepIndex } from "@/lib/crawl-steps";
import type { CrawlStatus, PipelineStep } from "@/lib/types";

interface StepRailProps {
  step: PipelineStep;
  status: CrawlStatus;
  activeLabel: string | null;
}

function nodeState(
  index: number,
  currentIndex: number,
  status: CrawlStatus,
): "pending" | "active" | "done" {
  if (status === "idle") return "pending";
  if (index < currentIndex) return "done";
  if (index === currentIndex && status === "running") return "active";
  if (index === currentIndex && (status === "done" || status === "error"))
    return status === "done" ? "done" : "active";
  if (index <= currentIndex) return "done";
  return "pending";
}

export function StepRail({ step, status, activeLabel }: StepRailProps) {
  const currentIndex =
    step === "idle" ? -1 : step === "done" ? PIPELINE_STEPS.length : stepIndex(step);

  const progress =
    status === "idle"
      ? 0
      : step === "done"
        ? 1
        : Math.max(0, (currentIndex + 0.5) / PIPELINE_STEPS.length);

  const indeterminate =
    status === "running" &&
    (step === "scrape" || step === "extract") &&
    !activeLabel?.includes("images");

  return (
    <div className="mt-4 space-y-2 font-sans" aria-live="polite" aria-atomic="false">
      <div className="relative h-0.5 w-full overflow-hidden rounded-full bg-paper-border/80">
        <motion.div
          className={`absolute inset-y-0 left-0 origin-left rounded-full ${
            indeterminate ? "shimmer-line w-full" : "bg-paper-accent/45"
          }`}
          initial={false}
          animate={{ scaleX: indeterminate ? 1 : progress }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          style={{ transformOrigin: "left" }}
        />
      </div>

      <div className="flex justify-between gap-1">
        {PIPELINE_STEPS.map((s, i) => {
          const ns = nodeState(i, currentIndex, status);
          return (
            <div
              key={s.id}
              className="group flex flex-1 flex-col items-center gap-1"
            >
              <motion.span
                className={`flex h-2 w-2 items-center justify-center rounded-full transition-colors ${
                  ns === "done"
                    ? "bg-paper-accent/40"
                    : ns === "active"
                      ? "bg-paper-accent/65 ring-2 ring-paper-accent/10"
                      : "bg-paper-border-soft"
                }`}
                animate={ns === "active" ? { scale: [1, 1.06, 1] } : { scale: 1 }}
                transition={
                  ns === "active"
                    ? { repeat: Infinity, duration: 2, ease: "easeInOut" }
                    : {}
                }
              />
              <span
                className={`text-[10px] tracking-wide uppercase transition-opacity ${
                  ns === "pending"
                    ? "opacity-0 group-hover:opacity-35"
                    : ns === "active"
                      ? "opacity-45"
                      : "opacity-30"
                }`}
              >
                {s.label}
              </span>
            </div>
          );
        })}
      </div>

      {activeLabel && status === "running" && (
        <motion.p
          className="text-center text-xs text-paper-muted"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.42 }}
          exit={{ opacity: 0 }}
        >
          {activeLabel}
        </motion.p>
      )}
    </div>
  );
}
