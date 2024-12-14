/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/ui.js", "./static/file_list.js"],
  theme: {
    extend: {
      boxShadow: {
        'md': '0 3px 7px rgba(0, 0, 0, 0.1)',
        'lg': '2px 4px 9px rgba(0, 0, 0, 0.12)',

      },
      borderWidth: {
        1: '1px'
      },
      colors: {
        blue: {
          50: '#EBF9FF',
          100: '#E4F2F8',
          200: '#ADE7FF',
          300: '#85DAFF',
          400: '#5CCEFF',
          500: '#33C2FF',
          600: '#0AB6FF',
          700: '#009DE0',
          800: '#0081B8',
          900: '#00567A',
        },
        zinc: {
          950: '#141414'
        }
      },
      fontFamily: {
        baloo: ['"Baloo 2"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}