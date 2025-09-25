# Willow v7 UI Components

## Overview

This document provides documentation for the core UI components in the Willow v7 desktop application.

## Components

### NavBar

The navigation bar provides tab-based navigation and search functionality.

**Props:**
- `activeTab` (string, required): Currently active tab
- `onTabClick` (function, required): Callback when a tab is clicked
- `onSearch` (function, required): Callback when search is submitted

**Features:**
- Tab navigation
- Search functionality
- Theme switching (planned)

### ModelSwitcher

The model switcher allows users to select between different AI models and toggle chained mode.

**Props:**
- `models` (array, required): List of available models
- `activeModelId` (string, required): ID of the currently active model
- `chainedMode` (boolean, required): Whether chained mode is enabled
- `onSelect` (function, required): Callback when a model is selected
- `onToggleChained` (function, required): Callback when chained mode is toggled

**Features:**
- Model selection dropdown
- Model status indicators (local/remote/down)
- Chained mode toggle
- Performance metrics display

### ChatMessage

The chat message component displays individual messages in the chat interface.

**Props:**
- `id` (string, required): Unique identifier for the message
- `author` (string, required): Author of the message (ai|user|system)
- `avatarUrl` (string, optional): URL for custom avatar image
- `content` (string, required): Message content (markdown)
- `timeISO` (string, required): Timestamp in ISO format
- `metadata` (object, optional): Additional metadata (model, tokensUsed)
- `collapsed` (boolean, optional): Whether the message is collapsed

**Features:**
- Markdown rendering
- Copy to clipboard functionality
- Collapse/expand toggle
- ARIA roles for accessibility
- Author-specific styling

## Design Tokens

The components use design tokens defined in `src/lib/willow-tokens.json` for consistent styling across themes.

## Accessibility

All components follow WCAG 2.1 AA guidelines and include:
- Proper ARIA roles and attributes
- Keyboard navigation support
- Sufficient color contrast
- Focus management

## Testing

Components are tested using:
- Unit tests with Vitest
- React Testing Library for component testing
- Accessibility testing with axe-core