import { type ReactNode } from "react";

interface PageHeaderProps {
  eyebrow: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}

export function PageHeader({ eyebrow, title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 px-6 md:px-10 pt-8 pb-6 border-b border-line">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1 className="font-display text-3xl md:text-4xl text-ink mt-1">{title}</h1>
        {description && <p className="text-sm text-ink-muted mt-2 max-w-xl">{description}</p>}
      </div>
      {actions && <div className="flex gap-2 shrink-0">{actions}</div>}
    </div>
  );
}
