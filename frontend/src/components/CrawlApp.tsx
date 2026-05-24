"use client";

import { useState } from "react";
import { useCrawlStream } from "@/hooks/useCrawlStream";
import { useModelConfig } from "@/hooks/useModelConfig";
import { ConfigButton } from "./ConfigButton";
import { CopyButton } from "./CopyButton";
import { DescribeWhisper } from "./DescribeWhisper";
import { EmptyState } from "./EmptyState";
import { HealthDot } from "./HealthDot";
import { MarkdownDoc } from "./MarkdownDoc";
import { ModelConfigPanel } from "./ModelConfigPanel";
import { PaperSheet } from "./PaperSheet";
import { StepRail } from "./StepRail";
import { UrlBar } from "./UrlBar";

function shortModelId(id: string): string {
  const parts = id.split("/");
  return parts.length > 2 ? parts.slice(-2).join("/") : id;
}

export function CrawlApp() {
  const { state, startCrawl } = useCrawlStream();
  const { config, setConfig, reset, hydrated } = useModelConfig();
  const [configOpen, setConfigOpen] = useState(false);
  const running = state.status === "running";

  const pageTitle =
    state.result?.metadata &&
    typeof state.result.metadata === "object" &&
    "title" in state.result.metadata
      ? String(state.result.metadata.title)
      : undefined;

  return (
    <main className="mx-auto flex min-h-full max-w-3xl flex-col px-4 py-10 sm:px-6 sm:py-14">
      <header className="mb-8 flex items-start justify-between gap-4 font-sans">
        <div>
          <h1 className="font-display text-xl font-medium tracking-tight text-paper-ink-strong">
            clawcrawl
          </h1>
          {hydrated && (
            <p className="mt-1 text-[11px] text-paper-muted-soft">
              {shortModelId(config.textModel)} · {shortModelId(config.visionModel)}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <ConfigButton
            onClick={() => setConfigOpen(true)}
            disabled={running}
          />
          <HealthDot />
        </div>
      </header>

      <UrlBar
        disabled={running}
        onSubmit={(url) => startCrawl(url, config)}
      />

      <StepRail
        step={state.step}
        status={state.status}
        activeLabel={state.activeLabel}
      />

      <DescribeWhisper progress={state.describeProgress} running={running} />

      {state.error && (
        <p className="mt-3 text-center font-sans text-sm text-paper-error">
          {state.error.step}: {state.error.message}
        </p>
      )}

      <div className="mt-8 flex-1">
        {state.status === "idle" && !state.result && <EmptyState />}

        {running && !state.result && (
          <PaperSheet className="mt-2 animate-pulse">
            <div className="space-y-4">
              <div className="h-4 w-2/3 rounded bg-paper-border/60" />
              <div className="h-3 w-full rounded bg-paper-border/40" />
              <div className="h-3 w-full rounded bg-paper-border/40" />
              <div className="h-3 w-4/5 rounded bg-paper-border/40" />
            </div>
          </PaperSheet>
        )}

        {state.result && (
          <PaperSheet className="mt-2">
            <div className="mb-6 flex items-center justify-end gap-2 border-b border-paper-border-soft pb-4">
              <CopyButton text={state.result.markdown} />
            </div>
            <MarkdownDoc markdown={state.result.markdown} title={pageTitle} />
          </PaperSheet>
        )}
      </div>

      <ModelConfigPanel
        open={configOpen}
        config={config}
        onClose={() => setConfigOpen(false)}
        onSave={setConfig}
        onReset={reset}
      />
    </main>
  );
}
