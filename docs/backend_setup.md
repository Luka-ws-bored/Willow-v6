# Backend Setup Guide

This guide explains how to set up the Willow backend with proper CORS configuration for communication with the frontend.

## Overview

The backend is a Flask application that serves API endpoints for the Willow desktop application. It includes proper CORS configuration to allow cross-origin requests from the frontend.

## Key Features

1. **CORS Configuration**: Allows requests only from the frontend origin (`http://localhost:5173`)
2. **API Endpoints**: Provides health check and data handling endpoints
3. **Existing Functionality**: Maintains all existing Willow backend functionality

## CORS Configuration

The backend is configured with strict CORS policies:

```python
from flask_cors import CORS

app = Flask(__name__)
# Allow CORS only from your frontend origin (dev), not everybody
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
```

This configuration:
- Only allows requests from `http://localhost:5173`
- Supports credentials (cookies, authorization headers, etc.)
- Handles preflight requests automatically

## API Endpoints

### New Endpoints

1. **`GET /api/health`**
   - Health check endpoint
   - Returns: `{"status": "ok"}`

2. **`POST /api/data`**
   - Data handling endpoint
   - Accepts JSON payload
   - Returns the received data: `{"received": payload}`

### Existing Endpoints

1. **`POST /chat`**
   - Chat endpoint for LLM interactions
   - Accepts message in JSON format
   - Returns generated response

2. **`POST /ingest`**
   - Document ingestion endpoint
   - Accepts document data for processing
   - Integrates with vector database

3. **`GET /health`**
   - Original health check endpoint
   - Returns service status information

4. **`GET /llm/status`**
   - LLM connection status endpoint
   - Checks connection to Ollama or other LLM providers

## Environment Variables

The backend uses the following environment variables:

```env
FRONTEND_ORIGIN=http://localhost:5173
BACKEND_URL=http://localhost:5000
DATABASE_URL=sqlite:///deploy/n8n_data/database.sqlite
OLLAMA_API_URL=http://localhost:11434
```

## Running the Backend

### Development Mode

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run backend with debug mode
python backend.py
```

The backend will start on `http://127.0.0.1:5000` with debug mode enabled.

### Production Mode

For production deployment, modify the run configuration:

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

## Testing the Backend

### Automated Testing

Run the test script to verify all endpoints:

```bash
python test_backend_endpoints.py
```

### Manual Testing

1. **Health Check**:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Data Endpoint**:
   ```bash
   curl -X POST http://localhost:5000/api/data \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, Willow!"}'
   ```

3. **CORS Verification**:
   ```bash
   curl -H "Origin: http://localhost:5173" \
        -v http://localhost:5000/api/health
   ```

4. **Preflight Request**:
   ```bash
   curl -X OPTIONS \
        -H "Origin: http://localhost:5173" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -v http://localhost:5000/api/data
   ```

## Security Considerations

1. **Development Only**: The current CORS configuration is suitable for development but should be restricted in production.

2. **Origin Restriction**: Only allows requests from `http://localhost:5173` to prevent unauthorized access.

3. **Credentials Support**: Supports credentials for development convenience but should be reviewed for production.

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Verify `FRONTEND_ORIGIN` in `.env.local` matches the frontend URL
   - Check that requests are being made from the correct origin

2. **Port Conflicts**:
   - Ensure no other services are using port 5000
   - Use `netstat -an | findstr "5000"` to check for conflicts

3. **Missing Dependencies**:
   - Ensure `flask-cors` is installed in the virtual environment
   - Run `pip install flask-cors` if needed

### Debugging Steps

1. Check if the backend is running:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. Verify CORS headers:
   ```bash
   curl -H "Origin: http://localhost:5173" -v http://localhost:5000/api/health
   ```

3. Check Flask debug output for error messages

## Integration with Frontend

The backend is designed to work with the Vite frontend running on `http://localhost:5173`. All API requests from the frontend should be made to the backend endpoints.

Example frontend request:
```javascript
fetch('http://localhost:5000/api/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({message: 'Hello from frontend!'})
})
.then(response => response.json())
.then(data => console.log(data));
```

## Integration with Tauri Desktop

When running in Tauri desktop mode, the frontend communicates with the backend via HTTP requests to `http://localhost:5000`. CORS is not an issue in this configuration since both the frontend and backend are running locally.