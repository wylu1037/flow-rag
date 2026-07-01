import Link from "next/link";
import type { ReactNode } from "react";

const navItems = [
  { href: "/chat", label: "Chat" },
  { href: "/documents", label: "Documents" },
  { href: "/datasets", label: "Datasets" },
  { href: "/settings", label: "Settings" }
];

export function AppFrame({ children }: { children: ReactNode }) {
  return (
    <main className="min-h-[100dvh] bg-background text-ink">
      <header className="border-b border-border bg-background">
        <div className="mx-auto flex min-h-16 max-w-[1200px] flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between md:px-6 md:py-0">
          <Link href="/chat" className="flex items-center gap-3 text-ink" aria-label="FlowRAG chat">
            <AnthropicMark />
            <span className="font-display text-[24px] leading-none tracking-[-0.03em]">
              FlowRAG
            </span>
          </Link>
          <nav className="flex flex-wrap items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-card hover:text-ink active:translate-y-[1px]"
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <span className="hidden rounded-full bg-card px-3 py-1 text-[13px] font-medium text-ink md:inline-flex">
              Local MVP
            </span>
            <Link
              href="/chat"
              className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary-active active:translate-y-[1px]"
            >
              Try chat
            </Link>
          </div>
        </div>
      </header>
      <div className="mx-auto w-full max-w-[1200px] px-4 py-8 md:px-6 md:py-10">{children}</div>
    </main>
  );
}

function AnthropicMark() {
  return (
    <svg className="h-7 w-7 text-ink" viewBox="0 0 32 32" aria-hidden="true">
      <path
        fill="currentColor"
        d="M15 2h2l.72 10.7 7.58-7.58 1.42 1.42-7.58 7.58L30 14.84v2.32l-10.86.72 7.58 7.58-1.42 1.42-7.58-7.58L17 30h-2l-.72-10.7-7.58 7.58-1.42-1.42 7.58-7.58L2 17.16v-2.32l10.86-.72-7.58-7.58 1.42-1.42 7.58 7.58L15 2Z"
      />
    </svg>
  );
}
