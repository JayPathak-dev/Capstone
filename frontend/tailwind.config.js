/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#0B192C',
          deep: '#1E293B',
          card: '#0F172A',
          teal: '#0D9488',
          accent: '#0284C7',
          surface: '#1E293B',
          border: '#334155',
          lightBg: '#F8FAFC',
          lightCard: '#FFFFFF',
          lightBorder: '#E2E8F0',
        },
        risk: {
          low: '#10B981',       // Green
          moderate: '#F59E0B',  // Amber
          high: '#F97316',      // Orange
          critical: '#EF4444',  // Red
        }
      },
    },
  },
  plugins: [],
}
