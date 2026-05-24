import type { CrawlEventType, PipelineStep } from "./types";

export const PIPELINE_STEPS: { id: PipelineStep; label: string }[] = [
  { id: "scrape", label: "Scrape" },
  { id: "extract", label: "Extract" },
  { id: "describe", label: "Describe" },
  { id: "replace", label: "Replace" },
];

export function stepFromEvent(type: CrawlEventType): PipelineStep | null {
  switch (type) {
    case "scrape_started":
    case "scrape_done":
      return "scrape";
    case "extract_started":
    case "extract_done":
      return "extract";
    case "describe_started":
    case "describe_progress":
      return "describe";
    case "replace_started":
    case "replace_done":
      return "replace";
    case "crawl_done":
      return "done";
    default:
      return null;
  }
}

export function stepIndex(step: PipelineStep): number {
  return PIPELINE_STEPS.findIndex((s) => s.id === step);
}
