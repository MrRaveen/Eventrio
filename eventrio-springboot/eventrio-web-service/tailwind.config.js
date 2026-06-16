/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/main/resources/templates/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#F3F0FF',
          100: '#E5DFFF',
          200: '#C9BFFF',
          300: '#A899FF',
          400: '#8A72FF',
          500: '#6E50F7',
          600: '#5538E8',
          700: '#4229CC',
          800: '#2E1DA0',
          900: '#1C1175',
          950: '#0D0840',
        },
      },
      boxShadow: {
        premium: '0 4px 24px rgba(85, 56, 232, 0.08)',
        'premium-hover': '0 8px 32px rgba(85, 56, 232, 0.16)',
      },
    },
  },
  plugins: [],
};
