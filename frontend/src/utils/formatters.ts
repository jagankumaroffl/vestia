/** Format a 0.0–1.0 score as a percentage string, e.g. 0.873 → "87" */
export function formatScorePercent(score: number): string {
  return Math.round(score * 100).toString();
}

/** Format an ISO date string as e.g. "Jun 15" */
export function formatShortDate(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

/** Format a 0–1 fraction as a percentage label, e.g. 0.857 → "86%" */
export function formatPercent(fraction: number): string {
  return `${Math.round(fraction * 100)}%`;
}

/** Pluralize a count + noun, e.g. (1, "item") → "1 item", (3, "item") → "3 items" */
export function pluralize(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}
