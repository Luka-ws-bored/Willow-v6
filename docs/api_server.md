# Willow API Server

This document explains how to run and use the Willow FastAPI server.

## Prerequisites

Make sure you have all required dependencies installed:

```bash
pip install -r requirements.txt
```

## Running the Server

You can run the server in two ways:

### Method 1: Using Makefile
```bash
make run-server
```

### Method 2: Direct command
```bash
uvicorn cmd.willow_server.app:app --reload --port 8080
```

## API Endpoints

Once the server is running, you can access the following endpoints:

- `GET /` - Root endpoint
- `GET /status` - Health check endpoint
- `POST /api/v1/auth/token` - Authentication token endpoint
- `GET /api/v1/workspaces` - List workspaces
- `GET /api/v1/workspaces/{workspace_id}/items` - List items in a workspace
- `GET /api/v1/items/{item_id}` - Get item details
- `PATCH /api/v1/items/{item_id}` - Update an item
- `POST /api/v1/query` - Query items
- `POST /api/v1/chat` - Chat with LLM

## Testing

Run the API smoke tests with:

```bash
make test-api
```

Or directly:

```bash
pytest -q tests/test_api_smoke.py
```

## Development

The server includes fallback mechanisms for development:

1. If core modules are not available, it uses in-memory stores
2. If the LLM adapter is not available, chat endpoints will return 503

For development without Ollama, you can use the mock adapter by ensuring `core.llm_adapter` points to `core.llm_adapter_mock` during development.