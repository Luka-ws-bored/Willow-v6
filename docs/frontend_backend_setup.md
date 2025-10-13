# Frontend ↔ Backend Connection Setup Guide

This guide explains how to properly configure the connection between the Willow frontend (React/Vite) and backend (Flask) for reliable communication.

## Configuration Overview

### Ports and Origins

- **Backend**: `http://localhost:5000` (Flask server)
- **Frontend Dev Server**: `http://localhost:5173` (Vite dev server)
- **Frontend Origin for CORS**: `http://localhost:5173`

### Environment Variables

The following environment variables should be set in `.env.local`:

```env
# Database configuration
DATABASE_URL=sqlite:///deploy/n8n_data/database.sqlite

# Ollama API URL
OLLAMA_API_URL=http://localhost:11434

# Frontend-backend communication
FRONTEND_ORIGIN=http://localhost:5173
BACKEND_URL=http://localhost:5000
```

## Backend Configuration

### CORS Setup

The backend is configured to accept requests from the frontend origin:

```python
from flask_cors import CORS
import os

frontend_origin = os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173')
CORS(app, origins=[frontend_origin])
```

### Endpoints

The backend exposes the following key endpoints:

1. `GET /health` - Health check endpoint
2. `POST /chat` - Chat endpoint for LLM interactions
3. `POST /ingest` - Document ingestion endpoint
4. `GET /llm/status` - LLM status check endpoint

## Frontend Configuration

### Vite Configuration

The Vite configuration in `willow-tauri/frontend/vite.config.js` sets the dev server port:

```javascript
export default defineConfig({
  server: {
    port: 5173,
    strictPort: true,
  },
  // ... other configuration
})
```

### Tauri Configuration

The Tauri configuration in `willow-tauri/tauri.conf.json` points to the frontend dev server:

```json
{
  "build": {
    "devPath": "http://localhost:5173",
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build"
  }
}
```

## Testing the Connection

### 1. Start the Backend

```bash
# From project root
.\.venv\Scripts\Activate.ps1
python backend.py
```

The backend should start on `http://localhost:5000`.

### 2. Start the Frontend

```bash
# From willow-tauri/frontend
npm run dev
```

The frontend should start on `http://localhost:5173`.

### 3. Verify Connection

Run the test script to verify the connection:

```bash
# From project root
python test_frontend_backend.py
```

This script tests:
- Backend health endpoint
- CORS configuration
- Chat endpoint functionality

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure the `FRONTEND_ORIGIN` environment variable matches the frontend URL.

2. **Port Conflicts**: Ensure no other services are using ports 5000 or 5173.

3. **Environment Variables**: Verify `.env.local` exists and contains the correct values.

### Debugging Steps

1. Check if the backend is running:
   ```bash
   curl http://localhost:5000/health
   ```

2. Check if the frontend is running:
   ```bash
   curl http://localhost:5173
   ```

3. Check CORS headers:
   ```bash
   curl -H "Origin: http://localhost:5173" -v http://localhost:5000/health
   ```

## Tauri Desktop Integration

When running in Tauri desktop mode, the frontend is served by Tauri itself, so CORS is not an issue. However, the backend still needs to be accessible.

For Tauri desktop:
1. The frontend communicates with the backend via HTTP requests
2. The backend URL should be configurable to support both development and production environments

## Security Considerations

1. **Development Only**: The current CORS configuration is suitable for development but should be restricted in production.

2. **Environment-Specific Configuration**: Use different configurations for development, testing, and production environments.

3. **API Security**: Implement proper authentication and authorization for production use.

## Next Steps

1. Run the test script to verify the connection
2. Start both frontend and backend services
3. Access the application through the frontend at `http://localhost:5173`
4. For Tauri desktop, run `npx tauri dev` from the `willow-tauri` directory