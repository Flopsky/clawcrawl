"use client";

import { FormEvent, useState } from "react";

interface UrlBarProps {
  disabled?: boolean;
  onSubmit: (url: string) => void;
}

export function UrlBar({ disabled, onSubmit }: UrlBarProps) {
  const [value, setValue] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed.startsWith("http") ? trimmed : `https://${trimmed}`);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-2 rounded-2xl border border-paper-border-soft bg-paper-sheet px-4 py-2.5 transition-colors focus-within:border-paper-border"
    >
      <input
        type="url"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Paste a URL to crawl…"
        disabled={disabled}
        className="min-w-0 flex-1 bg-transparent font-sans text-[15px] text-paper-ink placeholder:text-paper-muted-soft outline-none disabled:opacity-50"
        aria-label="URL to crawl"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="shrink-0 rounded-xl border border-paper-accent/25 bg-paper-accent/90 px-4 py-1.5 font-sans text-sm font-medium text-paper-on-accent transition-colors hover:bg-paper-accent-hover/90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Crawl
      </button>
    </form>
  );
}
