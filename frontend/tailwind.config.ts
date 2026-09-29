import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        panel: "#FFFFFF",
        surface: "#F1F5F9",
        "surface-subtle": "#F8FAFC",
        border: "#E2E8F0",
        "border-subtle": "#EDF2F7",
        primary: {
          DEFAULT: "#0A4D3C",
          hover: "#083E30",
          light: "#E6F4EA",
          dark: "#052A20",
        },
        gold: {
          DEFAULT: "#C5A059",
          light: "#FDF8ED",
          dark: "#A4813B",
          border: "#EAD9B5",
        },
        financial: {
          gain: "#0D824D",
          "gain-bg": "#E8F5E9",
          loss: "#D32F2F",
          "loss-bg": "#FFEBEE",
          neutral: "#64748B",
          accent: "#2563EB"
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)",
        "card-hover": "0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04)",
        glass: "0 8px 32px 0 rgba(10, 77, 60, 0.06)",
      }
    },
  },
  plugins: [],
};

export default config;
