"use client";

interface ConfigButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export function ConfigButton({ onClick, disabled }: ConfigButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="rounded-lg border border-paper-border-soft bg-paper-sheet/60 p-2 font-sans text-paper-muted transition-colors hover:border-paper-border hover:text-paper-ink disabled:opacity-40"
      aria-label="Model settings"
      title="Model settings"
    >
      <svg
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden
      >
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
      </svg>
    </button>
  );
}
