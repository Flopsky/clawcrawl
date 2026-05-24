"use client";

import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useCallback, useRef, useState } from "react";
import { stepFromEvent } from "@/lib/crawl-steps";
import type {
  CrawlEvent,
  CrawlModelConfig,
  CrawlResult,
  CrawlStatus,
  DescribeProgress,
  PipelineStep,
} from "@/lib/types";

const STREAM_URL = "/api/v1/crawl/stream";

export interface CrawlStreamState {
  status: CrawlStatus;
  step: PipelineStep;
  describeProgress: DescribeProgress | null;
  result: CrawlResult | null;
  error: { step: string; message: string } | null;
  activeLabel: string | null;
}

const initialState: CrawlStreamState = {
  status: "idle",
  step: "idle",
  describeProgress: null,
  result: null,
  error: null,
  activeLabel: null,
};

function labelForEvent(event: CrawlEvent): string | null {
  switch (event.type) {
    case "scrape_started":
      return "Reading the page…";
    case "extract_started":
      return "Finding images…";
    case "describe_started":
      return "Describing images…";
    case "replace_started":
      return "Assembling document…";
    default:
      return null;
  }
}

function reduceEvent(
  prev: CrawlStreamState,
  event: CrawlEvent,
): CrawlStreamState {
  const nextStep = stepFromEvent(event.type);
  let state: CrawlStreamState = {
    ...prev,
    step: nextStep ?? prev.step,
    activeLabel: labelForEvent(event) ?? prev.activeLabel,
  };

  if (event.type === "describe_progress") {
    const current = Number(event.data.index ?? 0);
    const total = Number(event.data.total ?? 0);
    state = {
      ...state,
      step: "describe",
      describeProgress: {
        current,
        total,
        url: String(event.data.url ?? ""),
        ok: Boolean(event.data.ok),
      },
    };
  }

  if (event.type === "crawl_done") {
    const result = event.data.result as CrawlResult;
    return {
      status: "done",
      step: "done",
      describeProgress: null,
      result,
      error: null,
      activeLabel: null,
    };
  }

  if (event.type === "crawl_error") {
    return {
      status: "error",
      step: prev.step,
      describeProgress: null,
      result: null,
      error: {
        step: String(event.data.step ?? "crawl"),
        message: String(event.data.message ?? "Unknown error"),
      },
      activeLabel: null,
    };
  }

  return state;
}

export function useCrawlStream() {
  const [state, setState] = useState<CrawlStreamState>(initialState);
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setState(initialState);
  }, []);

  const startCrawl = useCallback(async (url: string, models: CrawlModelConfig) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({
      status: "running",
      step: "scrape",
      describeProgress: null,
      result: null,
      error: null,
      activeLabel: "Starting…",
    });

    try {
      await fetchEventSource(STREAM_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url,
          text_model: models.textModel,
          vision_model: models.visionModel,
        }),
        signal: controller.signal,
        onmessage(msg) {
          if (!msg.data) return;
          const event = JSON.parse(msg.data) as CrawlEvent;
          setState((prev) => reduceEvent(prev, event));
        },
        onerror(err) {
          if (controller.signal.aborted) return;
          setState((prev) => ({
            ...prev,
            status: "error",
            error: {
              step: prev.step,
              message: err instanceof Error ? err.message : "Stream failed",
            },
            activeLabel: null,
          }));
          throw err;
        },
      });
    } catch (err) {
      if (controller.signal.aborted) return;
      setState((prev) => ({
        ...prev,
        status: "error",
        error: {
          step: prev.step,
          message: err instanceof Error ? err.message : "Request failed",
        },
        activeLabel: null,
      }));
    }
  }, []);

  return { state, startCrawl, reset };
}
