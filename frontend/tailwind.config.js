/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // A calm slate + deep teal palette for an internal support tool —
        // deliberately restrained, not a generic SaaS purple/gradient kit.
        brand: {
          50: '#eefbfa', 100: '#d4f3f1', 200: '#aee6e2', 300: '#78d2cb',
          400: '#42b6ac', 500: '#279a91', 600: '#1c7b74', 700: '#1a625d',
          800: '#194f4c', 900: '#184240',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
