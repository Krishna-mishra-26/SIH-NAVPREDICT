/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'space-dark': '#0a1428',
        'space-blue': '#1a3a5c',
        'neon-blue': '#00e0ff',
        'neon-yellow': '#ffd700',
        'space-purple': '#8b5cf6',
      },
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
      },
      animation: {
        'orbit': 'orbit 20s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        orbit: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: 1, textShadow: '0 0 10px #00e0ff' },
          '50%': { opacity: 0.8, textShadow: '0 0 20px #00e0ff' },
        },
      },
    },
  },
  plugins: [],
}
