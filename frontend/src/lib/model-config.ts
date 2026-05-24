import type { CrawlModelConfig } from "./types";

export const DEFAULT_MODEL_CONFIG: CrawlModelConfig = {
  textModel: "openrouter/google/gemini-2.0-flash-lite-001",
  visionModel: "openrouter/google/gemma-3-27b-it",
};

const STORAGE_KEY = "clawcrawl.models";

export function loadModelConfig(): CrawlModelConfig {
  if (typeof window === "undefined") return DEFAULT_MODEL_CONFIG;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_MODEL_CONFIG;
    const parsed = JSON.parse(raw) as Partial<CrawlModelConfig>;
    return {
      textModel: parsed.textModel ?? DEFAULT_MODEL_CONFIG.textModel,
      visionModel: parsed.visionModel ?? DEFAULT_MODEL_CONFIG.visionModel,
    };
  } catch {
    return DEFAULT_MODEL_CONFIG;
  }
}

export function saveModelConfig(config: CrawlModelConfig): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

export function resetModelConfig(): CrawlModelConfig {
  localStorage.removeItem(STORAGE_KEY);
  return { ...DEFAULT_MODEL_CONFIG };
}
