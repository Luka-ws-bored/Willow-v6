# Willow v7 Animations

## Overview

This document provides documentation for the animation system in the Willow v7 desktop application.

## Framer Motion Variants

Animations are implemented using Framer Motion variants defined in `src/variants/framerVariants.js`.

### thinkingPulse

A subtle pulsing animation for indicating thinking/loading states.

**Properties:**
- `initial`: { opacity: 0.6, scale: 0.995 }
- `animate`: { opacity: 1, scale: 1.0, transition: { repeat: Infinity, repeatType: 'mirror', duration: 1.2 } }

**Usage:**
```jsx
<motion.div
  variants={thinkingPulse}
  initial="initial"
  animate="animate"
>
  Thinking...
</motion.div>
```

### panelSlideFade

A slide and fade animation for panels and components.

**Properties:**
- `initial`: { x: 8, opacity: 0 }
- `animate`: { x: 0, opacity: 1, transition: { duration: 0.18 } }
- `exit`: { x: 8, opacity: 0, transition: { duration: 0.12 } }

**Usage:**
```jsx
<motion.div
  variants={panelSlideFade}
  initial="initial"
  animate="animate"
  exit="exit"
>
  Content
</motion.div>
```

### agentHandoffLine

An animation for drawing SVG path lines.

**Properties:**
- `initial`: { pathLength: 0 }
- `animate`: { pathLength: 1, transition: { duration: 0.6 } }

**Usage:**
```jsx
<motion.path
  variants={agentHandoffLine}
  initial="initial"
  animate="animate"
  d="M10 10 L100 100"
/>
```

## CSS Animations

Additional animations are implemented using CSS:

### Bounce Animation

Used for loading indicators and subtle UI feedback.

**Implementation:**
```css
.animate-bounce {
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
```

## Usage Guidelines

1. **Performance**: Use variants for complex animations to optimize performance
2. **Consistency**: Stick to the defined animation durations and easing curves
3. **Accessibility**: Respect `prefers-reduced-motion` media query
4. **Purpose**: Use animations to enhance UX, not distract from it

## Customization

To create new animations, add variants to `src/variants/framerVariants.js` following the existing patterns.