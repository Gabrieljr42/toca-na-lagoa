/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      colors: {
        brand: {
          50: '#ecfdf7',
          100: '#d1fae9',
          200: '#a7f3d6',
          300: '#6ee7bf',
          400: '#34d3a0',
          500: '#10b98a',
          600: '#059673',
          700: '#047860',
          800: '#065f4d',
          900: '#064e40',
        },
      },
    },
  },
};
