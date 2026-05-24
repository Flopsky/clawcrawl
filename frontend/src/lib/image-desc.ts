export interface ImageDescPayload {
  url: string;
  description: string;
}

export interface ParsedDescription {
  metaType: string;
  title: string;
  summary: string;
  raw: string;
  isError: boolean;
}

export function parseImageDescBlock(raw: string): ParsedDescription | null {
  try {
    const outer = JSON.parse(raw) as ImageDescPayload;
    let inner: { _meta?: { type?: string; title?: string }; data?: unknown } =
      {};
    try {
      inner = JSON.parse(outer.description) as typeof inner;
    } catch {
      return {
        metaType: "text",
        title: outer.url,
        summary: outer.description.slice(0, 160),
        raw: outer.description,
        isError: false,
      };
    }
    const metaType = inner._meta?.type ?? "unknown";
    const title = inner._meta?.title ?? new URL(outer.url).pathname.split("/").pop() ?? "Image";
    const isError = metaType === "error";
    const summary =
      isError && inner.data && typeof inner.data === "object" && "message" in inner.data
        ? String((inner.data as { message: string }).message)
        : `${metaType}${title ? ` · ${title}` : ""}`;
    return {
      metaType,
      title,
      summary,
      raw: outer.description,
      isError,
    };
  } catch {
    return null;
  }
}

const IMAGE_DESC_BLOCK =
  /<!-- image-desc:([\s\S]*?) -->(?:\s*\*?\[Image:[\s\S]*?\*\s*)?/g;

export type MarkdownSegment =
  | { kind: "markdown"; content: string }
  | { kind: "image-desc"; raw: string; parsed: ParsedDescription | null };

export function splitMarkdownSegments(markdown: string): MarkdownSegment[] {
  const segments: MarkdownSegment[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  const re = new RegExp(IMAGE_DESC_BLOCK.source, "g");
  while ((match = re.exec(markdown)) !== null) {
    if (match.index > lastIndex) {
      segments.push({
        kind: "markdown",
        content: markdown.slice(lastIndex, match.index),
      });
    }
    const raw = match[1];
    segments.push({
      kind: "image-desc",
      raw,
      parsed: parseImageDescBlock(raw),
    });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < markdown.length) {
    segments.push({ kind: "markdown", content: markdown.slice(lastIndex) });
  }

  return segments;
}
