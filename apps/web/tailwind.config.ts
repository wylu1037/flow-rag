import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        body: "hsl(var(--body))",
        "body-strong": "hsl(var(--body-strong))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          active: "hsl(var(--primary-active))",
          foreground: "hsl(var(--primary-foreground))"
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))"
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))"
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
          soft: "hsl(var(--muted-soft))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))"
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))"
        },
        surface: {
          soft: "hsl(var(--surface-soft))",
          cream: "hsl(var(--surface-cream-strong))",
          dark: "hsl(var(--surface-dark))",
          "dark-elevated": "hsl(var(--surface-dark-elevated))",
          "dark-soft": "hsl(var(--surface-dark-soft))"
        },
        on: {
          dark: "hsl(var(--on-dark))",
          "dark-soft": "hsl(var(--on-dark-soft))"
        },
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        ink: "hsl(var(--foreground))",
        fog: "hsl(var(--background))",
        moss: "hsl(var(--primary))",
        line: "hsl(var(--border))"
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-geist-sans)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "SFMono-Regular"]
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)"
      },
      boxShadow: {
        panel: "0 1px 3px rgba(20, 20, 19, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
