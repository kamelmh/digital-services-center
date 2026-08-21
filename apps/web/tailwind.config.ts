import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#0A1628",
        gold: "#D4AF37",
        ink: "#1A1A1A",
      },
    },
  },
  plugins: [],
};
export default config;
