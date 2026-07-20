/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Vazirmatn", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Cormorant Garamond", "Georgia", "serif"],
      },
      colors: {
        /* Exact brand green from Saleh Ayoubi identity */
        court: {
          DEFAULT: "#0d2d28",
          50: "#f3f7f6",
          100: "#e4eeeb",
          200: "#c5d9d3",
          300: "#9bbdb3",
          400: "#6a978c",
          500: "#4a7a6e",
          600: "#386157",
          700: "#2d4e46",
          800: "#1a3a34",
          900: "#0d2d28",
          950: "#071916",
        },
        ivory: {
          DEFAULT: "#f7f4ef",
          soft: "#faf8f5",
          mute: "#e8e2d8",
        },
      },
      letterSpacing: {
        brand: "0.28em",
        luxury: "0.4em",
      },
      fontWeight: {
        light: "300",
      },
      animation: {
        reveal: "reveal 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "reveal-slow": "reveal 1.6s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        kenburns: "kenburns 22s ease-out forwards",
        "line-grow": "lineGrow 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        marquee: "marquee 48s linear infinite",
        "scroll-bounce": "scrollBounce 2s ease-in-out infinite",
      },
      keyframes: {
        reveal: {
          "0%": { opacity: "0", transform: "translateY(32px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        kenburns: {
          "0%": { transform: "scale(1.08)" },
          "100%": { transform: "scale(1)" },
        },
        lineGrow: {
          "0%": { transform: "scaleX(0)" },
          "100%": { transform: "scaleX(1)" },
        },
        marquee: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        scrollBounce: {
          "0%, 100%": { transform: "translateY(0)", opacity: "0.4" },
          "50%": { transform: "translateY(8px)", opacity: "0.85" },
        },
      },
      transitionDuration: {
        2000: "2000ms",
        3000: "3000ms",
      },
    },
  },
  plugins: [],
};
