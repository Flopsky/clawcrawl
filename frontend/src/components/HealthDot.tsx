"use client";

import { useEffect, useState } from "react";

export function HealthDot() {
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/health")
      .then((r) => {
        if (!cancelled) setOk(r.ok);
      })
      .catch(() => {
        if (!cancelled) setOk(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const color =
    ok === null
      ? "bg-paper-muted/40"
      : ok
        ? "bg-emerald-600/70"
        : "bg-paper-error/70";

  return (
    <span
      className={`inline-block h-2 w-2 rounded-full ${color} transition-colors duration-500`}
      title={ok === null ? "Checking API…" : ok ? "API online" : "API offline"}
      aria-hidden
    />
  );
}
