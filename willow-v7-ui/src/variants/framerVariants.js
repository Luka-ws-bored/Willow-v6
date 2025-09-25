export const thinkingPulse = {
  initial: { opacity: 0.6, scale: 0.995 },
  animate: { opacity: 1, scale: 1.0, transition: { repeat: Infinity, repeatType: 'mirror', duration: 1.2 } }
};

export const panelSlideFade = {
  initial: { x: 8, opacity: 0 },
  animate: { x: 0, opacity: 1, transition: { duration: 0.18 } },
  exit: { x: 8, opacity: 0, transition: { duration: 0.12 } }
};

export const agentHandoffLine = {
  initial: { pathLength: 0 },
  animate: { pathLength: 1, transition: { duration: 0.6 } }
};