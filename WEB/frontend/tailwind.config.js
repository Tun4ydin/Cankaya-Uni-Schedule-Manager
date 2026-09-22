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
        cankaya: {
          navy: {
            DEFAULT: '#0f172a',
            dark: '#020617',
            light: '#1e293b',
            subtle: '#fefce8'
          },
          gold: {
            DEFAULT: '#eab308',
            dark: '#ca8a04',
            light: '#fde047',
            subtle: '#fefce8',
            accent: '#ffd000'
          }
        },
        darkbg: {
          DEFAULT: '#09090b',
          surface: '#111114',
          card: '#17171b',
          border: '#26262b',
          hover: '#202025'
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(234, 179, 8, 0.08)',
        'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.8)',
        'glow-gold': '0 0 20px rgba(234, 179, 8, 0.35)',
        'glow-yellow': '0 0 20px rgba(250, 204, 21, 0.4)',
      }
    },
  },
  plugins: [],
}
