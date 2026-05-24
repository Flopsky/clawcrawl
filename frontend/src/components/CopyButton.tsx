"use client";

import { useCallback, useState } from "react";

interface CopyButtonProps {
  text: string;
  className?: string;
}

export function CopyButton({ text, className = "" }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }, [text]);

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={`rounded-lg border border-paper-border-soft bg-paper-card/50 px-3 py-1.5 font-sans text-xs text-paper-muted transition-colors hover:border-paper-border hover:text-paper-ink ${className}`}
      aria-live="polite"
    >
      {copied ? "Copied" : "Copy"}
    </button>
  );
}
