"use client";

import { useCallback, useEffect, useState } from "react";
import {
  DEFAULT_MODEL_CONFIG,
  loadModelConfig,
  resetModelConfig,
  saveModelConfig,
} from "@/lib/model-config";
import type { CrawlModelConfig } from "@/lib/types";

export function useModelConfig() {
  const [config, setConfigState] = useState<CrawlModelConfig>(DEFAULT_MODEL_CONFIG);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setConfigState(loadModelConfig());
    setHydrated(true);
  }, []);

  const setConfig = useCallback((next: CrawlModelConfig) => {
    setConfigState(next);
    saveModelConfig(next);
  }, []);

  const reset = useCallback(() => {
    const defaults = resetModelConfig();
    setConfigState(defaults);
    return defaults;
  }, []);

  return {
    config,
    setConfig,
    reset,
    defaults: DEFAULT_MODEL_CONFIG,
    hydrated,
  };
}
