"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { splitMarkdownSegments } from "@/lib/image-desc";
import { ImageInsight } from "./ImageInsight";

interface MarkdownDocProps {
  markdown: string;
  title?: string;
}

export function MarkdownDoc({ markdown, title }: MarkdownDocProps) {
  const segments = splitMarkdownSegments(markdown);

  return (
    <div className="prose-paper max-w-none">
      {title && (
        <h1 className="mb-8 font-display text-3xl font-medium tracking-tight text-paper-ink">
          {title}
        </h1>
      )}
      {segments.map((seg, i) =>
        seg.kind === "markdown" ? (
          <ReactMarkdown key={i} remarkPlugins={[remarkGfm]}>
            {seg.content}
          </ReactMarkdown>
        ) : (
          <ImageInsight key={i} parsed={seg.parsed} raw={seg.raw} />
        ),
      )}
    </div>
  );
}
