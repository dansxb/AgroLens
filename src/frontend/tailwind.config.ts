import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // -------------------------------------------------------
        // AgroLens brand palette
        // Primary: verdant greens representing healthy crops
        // Accent: amber / earth tones representing soil and alerts
        // -------------------------------------------------------
        agrolens: {
          // Primary greens — healthy vegetation
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a", // Primary brand colour
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
          950: "#052e16",
        },
        earth: {
          // Earth / soil tones — secondary palette
          50: "#fefce8",
          100: "#fef9c3",
          200: "#fef08a",
          300: "#fde047",
          400: "#facc15",
          500: "#eab308",
          600: "#ca8a04", // Amber accent
          700: "#a16207",
          800: "#854d0e",
          900: "#713f12",
          950: "#422006",
        },
        // -------------------------------------------------------
        // Status colours (map directly to Tailwind semantic names
        // for consistency with health-status logic)
        // -------------------------------------------------------
        status: {
          healthy: "#22c55e",  // green — normal NDVI
          warning: "#f59e0b",  // amber — mild stress (10-15% below avg)
          alert: "#ef4444",    // red — significant stress (>15% below avg)
          unknown: "#94a3b8",  // slate — no data yet
        },
        // -------------------------------------------------------
        // Zone colours (VRA prescription map)
        // -------------------------------------------------------
        zone: {
          low: "#22c55e",     // Low application rate — green
          medium: "#f59e0b",  // Medium application rate — amber
          high: "#ef4444",    // High application rate — red
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
      },
      spacing: {
        // Sidebar width
        sidebar: "240px",
        // Top navigation height
        topnav: "64px",
      },
      screens: {
        // Tablet landscape breakpoint (10-inch, 1280×800)
        tablet: "1024px",
      },
    },
  },
  plugins: [],
};

export default config;
