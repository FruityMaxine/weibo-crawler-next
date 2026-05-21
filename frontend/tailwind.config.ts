import type { Config } from "tailwindcss";

// Linear DESIGN.md 暗色调 —— 直接对应色板
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas:     "#010102",
        surface:    "#0f1011",
        "surface-2":"#141516",
        "surface-3":"#18191a",
        hairline:   "#23252a",
        "hairline-strong":"#34343a",
        ink:        "#f7f8f8",
        "ink-muted":"#d0d6e0",
        "ink-subtle":"#8a8f98",
        "ink-tertiary":"#62666d",
        primary: {
          DEFAULT: "#5e6ad2",
          hover:   "#828fff",
          focus:   "#5e69d1",
        },
        success: "#27a644",
        danger:  "#d65555",
      },
      fontFamily: {
        sans: ["'Inter'", "SF Pro Display", "system-ui", "sans-serif"],
        display: ["'Inter'", "SF Pro Display", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "Menlo", "monospace"],
      },
      letterSpacing: {
        tightx: "-0.02em",
        tight2x: "-0.04em",
      },
      borderRadius: {
        xs: "4px", sm: "6px", md: "8px", lg: "12px", xl: "16px", xxl: "24px",
      },
      keyframes: {
        aurora: {
          "0%, 100%": { transform: "translate3d(0,0,0) rotate(0deg)" },
          "50%":      { transform: "translate3d(2%,2%,0) rotate(2deg)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "0.6" },
          "50%":      { opacity: "1" },
        },
      },
      animation: {
        aurora: "aurora 14s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
