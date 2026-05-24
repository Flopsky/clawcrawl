"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import type { DescribeProgress } from "@/lib/types";

interface DescribeWhisperProps {
  progress: DescribeProgress | null;
  running: boolean;
}

function hostnameFromUrl(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url.slice(0, 40);
  }
}

export function DescribeWhisper({ progress, running }: DescribeWhisperProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (progress && running) {
      setVisible(true);
      const t = setTimeout(() => setVisible(false), 2000);
      return () => clearTimeout(t);
    }
    if (!running) setVisible(false);
  }, [progress, running]);

  const show = progress && running && visible;

  return (
    <AnimatePresence>
      {show && (
        <motion.p
          className="mt-2 text-center font-sans text-xs text-paper-muted"
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 0.5, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.3 }}
        >
          {progress.current}/{progress.total} images
          <span className="text-paper-muted/60">
            {" "}
            · {hostnameFromUrl(progress.url)}
          </span>
        </motion.p>
      )}
    </AnimatePresence>
  );
}
