# Willow v7 Desktop UI

This is the Tauri-based desktop frontend for Willow v7.

## Prerequisites

- Node.js and npm
- Rust toolchain (for Tauri)
- Python (for backend integration)

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Make sure Rust is installed for Tauri:
   ```bash
   # Install rustup if you haven't already
   # Visit https://rustup.rs/ for installation instructions
   ```

## Development

1. Run the development version:
   ```bash
   npm run tauri:dev
   ```

2. Build the application:
   ```bash
   npm run tauri:build
   ```

## Port Configuration

The application is configured to run on port 5175 to avoid conflicts with other development servers.

## Troubleshooting

If you encounter issues with the desktop application not launching:

1. Make sure no other processes are using port 5175
2. Verify that Rust and Tauri CLI are properly installed
3. Check that all dependencies are installed with `npm install`
4. Ensure Python is available for backend integration

## Features

- **Three Main Screens**:
  - MainWorkspace: Chat interface with AI models
  - PromptVault: Store and manage prompts
  - RAGDashboard: Document ingestion and querying

- **Modern UI Components**:
  - Responsive design with TailwindCSS
  - Smooth animations with Framer Motion
  - Accessible components with proper ARIA attributes

- **Cross-Platform**:
  - Windows, Mac, and Linux support via Tauri

## Tech Stack

- React 18
- TailwindCSS
- Framer Motion
- Tauri
- Vite

## Getting Started

### Prerequisites

- Node.js 18+
- Rust (for Tauri)
- System dependencies for Tauri

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

### Build

```bash
npm run build
npm run tauri build
```

## Project Structure

```
src/
├── assets/          # Icons, images, and other assets
├── components/      # Reusable UI components
│   ├── atoms/       # Basic components
│   ├── molecules/   # Compound components
│   └── organisms/   # Complex components
├── screens/         # Main application screens
│   ├── MainWorkspace/
│   ├── PromptVault/
│   └── RAGDashboard/
├── lib/             # Utility functions and API clients
├── variants/        # Framer Motion animation variants
└── styles/          # Global styles and CSS variables
```

## Design System

- **Themes**: Forest (default), Cosmic, Cyberpunk
- **Typography**: Inter font family
- **Spacing**: Consistent spacing scale (xs, sm, md, lg, xl)
- **Colors**: Themeable color palette

## Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader compatibility
- Proper focus management

## Testing

- Unit tests with Vitest
- Component tests with React Testing Library
- Accessibility tests with axe-core
- Visual regression tests with Playwright

## License

MIT