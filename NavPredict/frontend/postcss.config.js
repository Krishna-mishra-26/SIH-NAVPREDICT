module.exports = {
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
    },
  },
  plugins: [],
}
