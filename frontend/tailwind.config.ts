import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F7F8F5",
        surface: "#FFFFFF",
        panel: "#FFFFFF",
        "surface-subtle": "#F0F2ED",
        border: "#E3E7E3",
        "border-subtle": "#EDF0EB",
        primary: {
          DEFAULT: "#12372A",
          hover: "#0D2A20",
          light: "#E7EEEB",
          dark: "#091D16",
        },
        secondary: {
          DEFAULT: "#2F5D50",
          hover: "#264B41",
          light: "#EBF2EF",
          dark: "#1C3830",
        },
        accent: {
          DEFAULT: "#C9A227",
          hover: "#B38F1E",
          light: "#FBF6E7",
          dark: "#967716",
        },
        gold: {
          DEFAULT: "#C9A227",
          light: "#FDF8ED",
          dark: "#967716",
          border: "#EADBB0",
        },
        content: {
          DEFAULT: "#17211B",
          muted: "#6B756E",
          subtle: "#8E9992",
        },
        financial: {
          gain: "#0D824D",
          "gain-bg": "#E8F5E9",
          loss: "#D32F2F",
          "loss-bg": "#FFEBEE",
          neutral: "#6B756E",
          "neutral-bg": "#F0F2ED",
          accent: "#2F5D50",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(18, 55, 42, 0.04), 0 1px 2px 0 rgba(18, 55, 42, 0.02)",
        "card-hover": "0 6px 16px -2px rgba(18, 55, 42, 0.08), 0 2px 6px -1px rgba(18, 55, 42, 0.04)",
        dropdown: "0 10px 25px -5px rgba(18, 55, 42, 0.1), 0 8px 10px -6px rgba(18, 55, 42, 0.05)",
        modal: "0 20px 25px -5px rgba(18, 55, 42, 0.15), 0 10px 10px -5px rgba(18, 55, 42, 0.06)",
        gold: "0 0 0 1px rgba(201, 162, 39, 0.3), 0 2px 8px rgba(201, 162, 39, 0.15)",
      },
    },
  },
  plugins: [],
};

export default config;
