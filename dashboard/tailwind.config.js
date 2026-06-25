/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#12141C",        // page background — dark ink-blue, not pure black
        surface: "#1B1E29",    // card surfaces
        "surface-alt": "#20242F",
        rule: "#2A2E3A",       // hairlines, borders
        marigold: "#E8A33D",   // primary accent — warm, not neon
        teal: "#4FB8AE",       // secondary accent — used for INT8 / "after" states
        ember: "#E2574C",      // reserved for sample-data warnings only
        ink2: "#8B8F9C",       // muted text
        paper: "#EDEDF0",      // primary text
      },
      fontFamily: {
        display: ["Hind", "system-ui", "sans-serif"],
        body: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        widest2: "0.18em",
      },
    },
  },
  plugins: [],
};
