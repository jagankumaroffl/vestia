/**
 * Maps backend named colors (from color_extractor.py's palette) to
 * approximate hex values for rendering color swatches in the UI.
 * Falls back to a mid-grey for unrecognized names.
 */
const COLOR_SWATCHES: Record<string, string> = {
  black: "#1A1A1A",
  "dark grey": "#3F3F3F",
  grey: "#7D7D7D",
  "light grey": "#BFBFBF",
  white: "#F2F0EC",

  "navy blue": "#1A2A4A",
  blue: "#2E5FAE",
  "light blue": "#8EC6E8",

  burgundy: "#5E1B28",
  red: "#B23A3A",
  pink: "#E5AEBE",

  orange: "#D9822B",
  yellow: "#E8C547",

  "dark green": "#2E4A2E",
  "olive green": "#707A3D",
  green: "#3F7A3F",
  "light green": "#A8D4A0",

  purple: "#6A4C8C",
  "light purple": "#C9B6DE",

  brown: "#5E4632",
  beige: "#D8CDB8",
};

export function colorSwatch(name: string | null | undefined): string {
  if (!name) return "#7D7D7D";
  const key = name.trim().toLowerCase();
  return COLOR_SWATCHES[key] || "#7D7D7D";
}

/** Whether the swatch is light enough to need a dark border for visibility. */
export function isLightColor(name: string | null | undefined): boolean {
  const hex = colorSwatch(name);
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.7;
}

/** Title-case a snake_case or lowercase label for display. */
export function titleCase(value: string): string {
  return value
    .split(/[_\s]+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
