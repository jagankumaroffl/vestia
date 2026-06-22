import type { Config } from "tailwindcss";

/**
 * Vestia design tokens — "Digital Atelier"
 *
 * A dark, editorial fashion-house palette. Warm ivory ink on near-black
 * canvas, antique gold as the single signature accent (used for scores
 * and primary actions), sage and clay as quiet secondary tag colors.
 */
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        canvas:  "#0E0D0C",
        surface: "#19181A",
        raised:  "#221F1E",
        line:    "#2E2B28",
        ink: {
          DEFAULT: "#F4F0E8",
          muted:   "#9A938A",
          faint:   "#6B6560",
        },
        gold: {
          DEFAULT: "#C9A227",
          dim:     "#8C7320",
          glow:    "#E6C75A",
        },
        sage: {
          DEFAULT: "#6E7B5E",
          dim:     "#4F5944",
          light:   "#9CAA8A",
        },
        clay: {
          DEFAULT: "#A6582F",
          dim:     "#7A4022",
          light:   "#CC8358",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans:    ["var(--font-sans)", "Helvetica", "Arial", "sans-serif"],
        mono:    ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tag: "0.18em",
      },
      borderRadius: {
        card: "2px",
      },
      boxShadow: {
        card: "0 1px 0 0 rgba(244,240,232,0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
