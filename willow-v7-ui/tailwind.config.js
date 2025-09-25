const tokens = require('./src/lib/willow-tokens.json');

module.exports = {
  content: ['./index.html','./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        willow: {
          primary: tokens.themes.forest.primary,
          card: tokens.themes.forest.card,
          bg: tokens.themes.forest.background,
          accent: tokens.themes.forest.accent,
          muted: tokens.themes.forest.muted,
          text: tokens.themes.forest.text
        }
      },
      borderRadius: {
        '2xl': tokens.radii["2xl"] + 'px'
      },
      boxShadow: {
        soft: tokens.shadows.soft,
        medium: tokens.shadows.medium
      }
    }
  },
  plugins: []
}