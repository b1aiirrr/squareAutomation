import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#090b11",
        panel: "#0f1420",
        accent: "#06b6d4",
        success: "#22c55e",
        warning: "#f59e0b",
        danger: "#f43f5e"
      },
      boxShadow: {
        neon: "0 0 24px rgba(6, 182, 212, 0.25)",
      },
    },
  },
  plugins: [],
} satisfies Config;
