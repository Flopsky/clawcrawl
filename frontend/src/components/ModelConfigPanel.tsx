"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { DEFAULT_MODEL_CONFIG } from "@/lib/model-config";
import type { CrawlModelConfig, OpenRouterModel } from "@/lib/types";

interface ModelConfigPanelProps {
  open: boolean;
  config: CrawlModelConfig;
  onClose: () => void;
  onSave: (config: CrawlModelConfig) => void;
  onReset: () => CrawlModelConfig;
}

function useDebounce<T>(value: T, ms: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(value), ms);
    return () => window.clearTimeout(t);
  }, [value, ms]);
  return debounced;
}

async function fetchModels(
  outputModalities: string,
): Promise<OpenRouterModel[]> {
  const params = new URLSearchParams({ output_modalities: outputModalities });
  const res = await fetch(`/api/v1/models?${params}`);
  if (!res.ok) throw new Error(`Failed to load models (${res.status})`);
  const json = (await res.json()) as { data: OpenRouterModel[] };
  return json.data ?? [];
}

function filterModels(models: OpenRouterModel[], query: string): OpenRouterModel[] {
  const q = query.trim().toLowerCase();
  if (!q) return models;
  return models.filter(
    (m) =>
      m.id.toLowerCase().includes(q) ||
      (m.name?.toLowerCase().includes(q) ?? false),
  );
}

function visionCapable(models: OpenRouterModel[]): OpenRouterModel[] {
  return models.filter((m) =>
    m.architecture?.input_modalities?.includes("image"),
  );
}

interface ModelPickerProps {
  label: string;
  hint: string;
  models: OpenRouterModel[];
  loading: boolean;
  error: string | null;
  selectedId: string;
  search: string;
  onSearchChange: (q: string) => void;
  onSelect: (id: string) => void;
}

function ModelPicker({
  label,
  hint,
  models,
  loading,
  error,
  selectedId,
  search,
  onSearchChange,
  onSelect,
}: ModelPickerProps) {
  const debouncedSearch = useDebounce(search, 150);
  const filtered = useMemo(
    () => filterModels(models, debouncedSearch).slice(0, 80),
    [models, debouncedSearch],
  );

  return (
    <section className="space-y-2">
      <div>
        <h3 className="font-sans text-sm font-medium text-paper-ink">{label}</h3>
        <p className="font-sans text-xs text-paper-muted-soft">{hint}</p>
      </div>
      <input
        type="search"
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        placeholder="Search models…"
        className="w-full rounded-lg border border-paper-border-soft bg-paper-card/40 px-3 py-2 font-sans text-sm text-paper-ink outline-none focus:border-paper-border"
      />
      <div className="max-h-40 overflow-y-auto rounded-lg border border-paper-border-soft bg-paper-card/30">
        {loading && (
          <p className="px-3 py-2 font-sans text-xs text-paper-muted">Loading…</p>
        )}
        {error && (
          <p className="px-3 py-2 font-sans text-xs text-paper-error">{error}</p>
        )}
        {!loading && !error && filtered.length === 0 && (
          <p className="px-3 py-2 font-sans text-xs text-paper-muted">No models found</p>
        )}
        {filtered.map((m) => (
          <button
            key={m.id}
            type="button"
            onClick={() => onSelect(m.id)}
            className={`block w-full border-b border-paper-border/50 px-3 py-2 text-left font-sans text-xs transition-colors last:border-0 hover:bg-paper-card/60 ${
              selectedId === m.id ? "bg-paper-card text-paper-ink" : "text-paper-muted"
            }`}
          >
            <span className="font-medium text-paper-ink">{m.name || m.id}</span>
            <span className="mt-0.5 block truncate text-paper-muted-soft">{m.id}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

export function ModelConfigPanel({
  open,
  config,
  onClose,
  onSave,
  onReset,
}: ModelConfigPanelProps) {
  const [draft, setDraft] = useState(config);
  const [textModels, setTextModels] = useState<OpenRouterModel[]>([]);
  const [visionModels, setVisionModels] = useState<OpenRouterModel[]>([]);
  const [textLoading, setTextLoading] = useState(false);
  const [visionLoading, setVisionLoading] = useState(false);
  const [textError, setTextError] = useState<string | null>(null);
  const [visionError, setVisionError] = useState<string | null>(null);
  const [textSearch, setTextSearch] = useState("");
  const [visionSearch, setVisionSearch] = useState("");

  useEffect(() => {
    if (open) setDraft(config);
  }, [open, config]);

  const loadModels = useCallback(async () => {
    setTextLoading(true);
    setVisionLoading(true);
    setTextError(null);
    setVisionError(null);
    try {
      const [text, visionRaw] = await Promise.all([
        fetchModels("text"),
        fetchModels("text,image"),
      ]);
      setTextModels(text);
      setVisionModels(visionCapable(visionRaw));
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load models";
      setTextError(msg);
      setVisionError(msg);
    } finally {
      setTextLoading(false);
      setVisionLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) loadModels();
  }, [open, loadModels]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-paper-ink/10 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="model-config-title"
      onClick={onClose}
    >
      <div
        className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-paper-border-soft bg-paper-sheet p-6"
        style={{ boxShadow: "var(--paper-shadow)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id="model-config-title"
          className="font-display text-lg font-medium text-paper-ink"
        >
          Model settings
        </h2>
        <p className="mt-1 font-sans text-xs text-paper-muted">
          Overrides apply to the next crawl. API key stays on the server.
        </p>

        <div className="mt-6 space-y-6">
          <ModelPicker
            label="Extract images"
            hint="Text model for finding image URLs in markdown"
            models={textModels}
            loading={textLoading}
            error={textError}
            selectedId={draft.textModel}
            search={textSearch}
            onSearchChange={setTextSearch}
            onSelect={(id) => setDraft((d) => ({ ...d, textModel: id }))}
          />
          <ModelPicker
            label="Describe images"
            hint="Vision model for multimodal image description"
            models={visionModels}
            loading={visionLoading}
            error={visionError}
            selectedId={draft.visionModel}
            search={visionSearch}
            onSearchChange={setVisionSearch}
            onSelect={(id) => setDraft((d) => ({ ...d, visionModel: id }))}
          />
        </div>

        <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => setDraft(onReset())}
            className="font-sans text-xs text-paper-muted underline-offset-2 hover:text-paper-accent hover:underline"
          >
            Reset to defaults
          </button>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-paper-border px-4 py-2 font-sans text-sm text-paper-muted hover:bg-paper-bg"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => {
                onSave(draft);
                onClose();
              }}
              className="rounded-lg border border-paper-accent/20 bg-paper-accent/85 px-4 py-2 font-sans text-sm font-medium text-paper-on-accent hover:bg-paper-accent-hover/90"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export { DEFAULT_MODEL_CONFIG };
