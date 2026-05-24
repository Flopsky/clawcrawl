"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface PaperSheetProps {
  children: ReactNode;
  className?: string;
}

export function PaperSheet({ children, className = "" }: PaperSheetProps) {
  return (
    <motion.article
      className={`rounded-2xl border border-paper-border-soft bg-paper-sheet px-6 py-8 sm:px-10 sm:py-10 ${className}`}
      style={{ boxShadow: "var(--paper-shadow)" }}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.article>
  );
}
