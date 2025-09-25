# Willow v7 Design System

## Overview

The Willow v7 design system provides a consistent visual language across the desktop application.

## Themes

### Forest (Default)

- Primary: #2C7A5B
- Secondary: #A1DAB4
- Background: #0F1614
- Card: #111715
- Accent: #6FB98F
- Muted: #9EB7AF
- Text: #E6F0EC

### Cosmic

- Primary: #4B0082
- Secondary: #9370DB
- Background: #0F1020
- Card: #151528
- Accent: #7F00FF
- Muted: #9CA0B8
- Text: #EFEFFF

### Cyberpunk

- Primary: #00FFFF
- Secondary: #FF00FF
- Background: #0D0D0D
- Card: #121212
- Accent: #FF4500
- Muted: #9EB7AF
- Text: #FFFFFF

## Typography

- Font Family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial
- Sizes:
  - H1: 32px
  - H2: 24px
  - H3: 18px
  - Body: 14px
- Weights:
  - Regular: 400
  - Medium: 500
  - Bold: 700

## Spacing

- XS: 4px
- SM: 8px
- MD: 16px
- LG: 24px
- XL: 32px

## Radius

- SM: 6px
- MD: 12px
- LG: 20px
- 2XL: 28px

## Shadows

- Soft: 0 6px 18px rgba(0,0,0,0.12)
- Medium: 0 10px 30px rgba(0,0,0,0.16)

## Z-Index

- Header: 60
- Footer: 50
- Modal: 999

## Implementation

The design system is implemented using:
- Tailwind CSS for styling
- CSS variables for theme switching
- Design tokens in `src/lib/willow-tokens.json`
- Global styles in `src/styles/globals.css`

## Usage

To use the design system in components:

```jsx
// Using Tailwind classes
<div className="bg-willow-bg text-willow-text p-4 rounded-lg">
  Content
</div>

// Using CSS variables
<div style={{ 
  backgroundColor: 'var(--color-bg)',
  color: 'var(--color-text)'
}}>
  Content
</div>
```

## Theme Switching

Theme switching is implemented using CSS classes on the body element:

- Default: No additional class
- Cosmic: `theme-cosmic`
- Cyberpunk: `theme-cyberpunk`

Components automatically adapt to the current theme through CSS variables.