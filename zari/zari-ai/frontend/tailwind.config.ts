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
        "royal-green": "#1A4D2E",
        "leaf-green": "#4F6F52",
        "off-white": "#F5EFE6",
        "pure-white": "#FFFFFF",
      },
    },
  },
  plugins: [],
};

export default config;
