"use client";

import { useState } from "react";
import type { ParsedDescription } from "@/lib/image-desc";

interface ImageInsightProps {
  parsed: ParsedDescription | null;
  raw: string;
}

export function ImageInsight({ parsed, raw }: ImageInsightProps) {
  const [expanded, setExpanded] = useState(false);

  if (!parsed) {
    return (
      <aside className="my-6 rounded-xl border border-paper-border bg-paper-card px-4 py-3 font-sans text-sm text-paper-muted">
        Image description unavailable
      </aside>
    );
  }

  const typeLabel = parsed.metaType;
  const isStructured =
    typeLabel === "diagram" ||
    typeLabel === "chart" ||
    typeLabel === "flowchart";

  return (
    <aside
      className={`my-6 rounded-xl border px-4 py-3 font-sans text-sm transition-colors ${
        parsed.isError
          ? "border-paper-error/25 bg-paper-card text-paper-error"
          : "border-paper-border-soft bg-paper-card text-paper-ink"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] uppercase tracking-wider text-paper-muted">
            {parsed.isError ? "Error" : typeLabel}
          </p>
          <p className="mt-0.5 font-medium text-paper-ink">{parsed.title}</p>
          <p className="mt-1 text-paper-muted">{parsed.summary}</p>
        </div>
        {(isStructured || parsed.raw.length > 120) && (
          <button
            type="button"
            onClick={() => setExpanded((e) => !e)}
            className="shrink-0 text-xs text-paper-accent hover:underline"
          >
            {expanded ? "Hide" : isStructured ? "Show structure" : "More"}
          </button>
        )}
      </div>
      {expanded && (
        <pre className="mt-3 max-h-48 overflow-auto rounded-lg bg-paper-sheet/80 p-3 text-[11px] leading-relaxed text-paper-muted">
          {tryFormatJson(parsed.raw)}
        </pre>
      )}
    </aside>
  );
}

function tryFormatJson(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    return raw;
  }
}
