import { titleCase } from "@/utils/colorUtils";

interface BreakdownBarsProps {
  data: Record<string, number>;
  maxRows?: number;
}

export function BreakdownBars({ data, maxRows = 6 }: BreakdownBarsProps) {
  const entries = Object.entries(data)
    .sort((a, b) => b[1] - a[1])
    .slice(0, maxRows);

  if (entries.length === 0) {
    return <p className="text-sm text-ink-faint">No data yet.</p>;
  }

  const max = Math.max(...entries.map(([, count]) => count));

  return (
    <div className="flex flex-col gap-2.5">
      {entries.map(([label, count]) => (
        <div key={label} className="flex items-center gap-3">
          <span className="text-xs text-ink-muted w-28 shrink-0 truncate">{titleCase(label)}</span>
          <div className="flex-1 h-1.5 bg-line rounded-full overflow-hidden">
            <div className="h-full bg-sage" style={{ width: `${(count / max) * 100}%` }} />
          </div>
          <span className="font-mono text-xs text-ink-muted w-6 text-right">{count}</span>
        </div>
      ))}
    </div>
  );
}
