/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: '#80b3ba',
          vivid: '#80b3ba',
          dark: '#5f8d93',
          darker: '#4d7378',
          deep: '#3d5c60',
          light: '#9bc4c9',
          pale: '#d7e9f2',
          bg: '#d7e9f2',
        },
        muted: '#1e293b',
        sage: '#334155',
      },
      fontFamily: {
        heading: ['Inter', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Inter', 'system-ui', 'sans-serif'],
      },
      letterSpacing: {
        sentence: '0.015em',
      },
    },
  },
  plugins: [],
}
