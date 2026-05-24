export interface CrawlModelConfig {
  textModel: string;
  visionModel: string;
}

export interface OpenRouterModel {
  id: string;
  name: string;
  description?: string;
  architecture?: {
    input_modalities?: string[];
    output_modalities?: string[];
  };
}

export type CrawlStatus = "idle" | "running" | "done" | "error";

export type PipelineStep =
  | "idle"
  | "scrape"
  | "extract"
  | "describe"
  | "replace"
  | "done";

export type CrawlEventType =
  | "crawl_started"
  | "scrape_started"
  | "scrape_done"
  | "extract_started"
  | "extract_done"
  | "describe_started"
  | "describe_progress"
  | "replace_started"
  | "replace_done"
  | "crawl_done"
  | "crawl_error";

export interface CrawlEvent {
  type: CrawlEventType;
  data: Record<string, unknown>;
}

export interface ImageDescription {
  url: string;
  description: string;
}

export interface CrawlResult {
  url: string;
  markdown: string;
  images: ImageDescription[];
  metadata: Record<string, unknown>;
}

export interface DescribeProgress {
  current: number;
  total: number;
  url: string;
  ok: boolean;
}
