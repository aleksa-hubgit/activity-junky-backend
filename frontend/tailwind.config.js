/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{vue,js,ts,jsx,tsx}", "./index.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
      gridTemplateColumns: {
        '70/30': '70% 28%',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

