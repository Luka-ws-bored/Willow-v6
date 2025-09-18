# Willow + n8n + Ollama Integration Instructions

This document provides step-by-step instructions for setting up and testing the full integration between Willow, n8n, and Ollama using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM recommended
- Basic understanding of Docker concepts

## Setup Instructions

### 1. Start the Docker Stack

From the root of the Willow project directory, run:

```bash
docker compose -f deploy/docker-compose.willow-n8n-ollama.yml up -d --build
```

This will start three services:
- **willow**: The Willow backend service on port 5000
- **n8n**: The n8n workflow automation tool on port 5678
- **ollama**: The Ollama LLM service on port 11434

### 2. Verify Containers are Running

Check that all containers are up and running:

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
```

Expected output should show `willow`, `n8n`, and `ollama` containers in the "Up" status.

### 3. Pull an Ollama Model (if needed)

If you don't have any models downloaded, you'll need to pull one:

```bash
docker exec -it ollama ollama pull llama3.1:8b
```

### 4. Test the Integration

Use the provided test script to verify all components are working together:

```bash
python test_n8n_integration.py
```

Or run the manual tests:

#### Test Ollama from inside the Willow container:
```bash
docker exec -it willow /bin/sh -c "curl -sS -X POST http://ollama:11434/api/generate -H 'Content-Type: application/json' -d '{\"model\":\"llama3.1:8b\",\"prompt\":\"ping\",\"max_tokens\":5}' | head -n 40"
```

#### Check Willow's environment variables:
```bash
docker exec -it willow /bin/sh -c "env | grep -i OLLAMA || true"
```

#### Test Willow's LLM status endpoint:
```bash
curl -sS http://localhost:5000/api/llm/status | jq .
```

## Integration Patterns

### Pattern A: Willow triggers n8n

1. Create a webhook in n8n (POST)
2. In Willow code, when an event occurs, POST to the n8n webhook URL

### Pattern B: n8n calls Willow

1. In n8n create an HTTP request node that posts to Willow endpoint:
   - URL: `http://willow:5000/api/chat` or `http://willow:5000/api/ingest`
   - Method: POST
   - Content-Type: application/json

Sample payload for chat:
```json
{
  "message": "Hello from n8n!"
}
```

Sample payload for document ingestion:
```json
{
  "document": "This is a document to be ingested into the vector database."
}
```

## Testing the Full RAG/Chat Loop

1. Send a quick generate to Ollama to confirm model runs:
   ```bash
   curl -sS -X POST http://localhost:11434/api/generate -H 'Content-Type: application/json' -d '{"model":"llama3.1:8b","prompt":"Say hello","max_tokens":20}' | head -n 40
   ```

2. In n8n, create a test flow:
   - Webhook -> HTTP Request to Willow /api/chat -> Respond
   - Call the n8n webhook with a JSON that contains 'user_input':
   ```bash
   curl -X POST "http://localhost:5678/webhook/YOUR_WEBHOOK_ID" -H 'Content-Type: application/json' -d '{"user_input":"hello, test"}'
   ```

3. Watch logs for Willow and Ollama:
   ```bash
   docker logs -f willow
   docker logs -f ollama
   ```

## Troubleshooting

### If containers fail to start:

1. Check the logs:
   ```bash
   docker logs willow
   docker logs ollama
   docker logs n8n
   ```

2. Verify port conflicts:
   ```bash
   netstat -an | grep -E "(5000|5678|11434)"
   ```

### If Ollama connection fails:

1. Check Ollama logs:
   ```bash
   docker logs ollama
   ```

2. Verify Ollama is serving on the correct interface:
   Look for "Listening on [::]:11434" in the logs

### If Willow shows "disconnected":

1. Check environment variables:
   ```bash
   docker exec willow env | grep -i OLLAMA
   ```

2. Test connectivity from within the container:
   ```bash
   docker exec -it willow /bin/sh -c "curl -sS http://ollama:11434/api/tags"
   ```

## Security Notes

- By default, Ollama does not require an API key
- The Ollama service is bound to 0.0.0.0, making it accessible on the host network
- For production deployments, consider:
  - Adding authentication to Ollama
  - Using a reverse proxy with authentication
  - Restricting network access with firewall rules

## Useful Commands

- **Stop the stack**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml down`
- **View logs**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml logs -f`
- **Restart a service**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml restart willow`
- **View running processes**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml top`