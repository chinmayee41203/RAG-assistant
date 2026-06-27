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
        bg: "#0d0d14",
        surface: "#111118",
        border: "rgba(255,255,255,0.07)",
        accent: "#7c3aed",
        "accent-light": "#a78bfa",
        "accent-blue": "#60a5fa",
        "accent-green": "#34d399",
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease",
        "slide-up": "slideUp 0.25s ease",
        blink: "blink 1s step-end infinite",
      },
      keyframes: {
        fadeIn: { from: { opacity: "0" }, to: { opacity: "1" } },
        slideUp: { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        blink: { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0" } },
      },
    },
  },
  plugins: [],
};
export default config;
