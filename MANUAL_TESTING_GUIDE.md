# Manual Testing Guide for Willow + n8n + Ollama Integration

This guide provides detailed instructions for manually testing the integration between Willow, n8n, and Ollama using Docker Compose.

## Prerequisites

Before starting, ensure you have:
- Docker Desktop installed and running
- Git Bash, PowerShell, or Command Prompt
- Basic knowledge of Docker commands

## Setup Instructions

### 1. Navigate to the Project Directory

Open your terminal and navigate to the Willow project root directory:

```bash
cd /path/to/Willow-v6
```

### 2. Start the Docker Stack

Run the following command to start all services:

```bash
docker compose -f deploy/docker-compose.willow-n8n-ollama.yml up -d --build
```

This command will:
- Build the Willow service from the Dockerfile
- Pull the n8n and Ollama images from Docker Hub
- Start all three services in detached mode

### 3. Verify Containers are Running

Check that all containers are up and running:

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
```

You should see output similar to:
```
NAMES                IMAGE                  STATUS         PORTS
willow               willow:latest          Up 2 minutes   0.0.0.0:5000->5000/tcp
n8n                  n8nio/n8n:latest       Up 2 minutes   0.0.0.0:5678->5678/tcp
ollama               ollama/ollama:latest   Up 2 minutes   0.0.0.0:11434->11434/tcp
```

### 4. Pull an Ollama Model

If you don't have any models downloaded, you'll need to pull one. We recommend using the llama3.1:8b model:

```bash
docker exec -it ollama ollama pull llama3.1:8b
```

This may take several minutes depending on your internet connection.

## Testing the Integration

### Test 1: Verify Ollama API from inside the Willow container

This test validates that Docker networking is working correctly:

```bash
docker exec -it willow /bin/sh -c "curl -sS -X POST http://ollama:11434/api/generate -H 'Content-Type: application/json' -d '{\"model\":\"llama3.1:8b\",\"prompt\":\"ping\",\"max_tokens\":5}' | head -n 40"
```

Expected output: A valid JSON response object from Ollama.

### Test 2: Check Ollama readiness and container logs

If the previous test failed, check the Ollama container logs:

```bash
docker logs -f ollama
```

Look for messages indicating the server is "serving" on port 11434.

### Test 3: Confirm Willow backend can reach Ollama

Check the environment variables in the Willow container:

```bash
docker exec -it willow /bin/sh -c "env | grep -i OLLAMA || true"
```

Expected output should include:
```
OLLAMA_API_URL=http://ollama:11434
OLLAMA_API_AUTH=
```

Test HTTP request to the configured URL:

```bash
docker exec -it willow /bin/sh -c "curl -sS ${OLLAMA_API_URL:-http://ollama:11434}/api/generate -d '{\"model\":\"llama3.1:8b\",\"prompt\":\"healthcheck\"}' | head -n 40"
```

### Test 4: Verify n8n is reachable

Open your web browser and navigate to:
```
http://localhost:5678
```

Login with the credentials:
- Username: admin
- Password: willow123

Create a test workflow with a Webhook node that responds "ok". Test the webhook with curl:

```bash
curl -X POST "http://localhost:5678/webhook/YOUR_WEBHOOK_ID" -H 'Content-Type: application/json' -d '{"test":"ok"}'
```

### Test 5: Wire Willow <-> n8n

#### Pattern A: Willow triggers n8n

1. Create a webhook in n8n (POST)
2. In Willow code, when an event occurs, POST to the n8n webhook URL

#### Pattern B: n8n calls Willow

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

### Test 6: Test the full RAG/chat loop

1. From your host, send a quick generate to Ollama to confirm model runs:
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

### Test 7: Frontend GUI connectivity check

If Willow GUI is a separate frontend that hits the Willow backend, confirm backend is connected:

API: check backend LLM status endpoint:
```bash
curl -sS http://localhost:5000/api/llm/status | jq .
```

Expected response:
```json
{
  "connected": true,
  "backend": "ollama",
  "url": "http://ollama:11434"
}
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

## Useful Commands

- **Stop the stack**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml down`
- **View logs**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml logs -f`
- **Restart a service**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml restart willow`
- **View running processes**: `docker compose -f deploy/docker-compose.willow-n8n-ollama.yml top`

## Security Notes

- By default, Ollama does not require an API key
- The Ollama service is bound to 0.0.0.0, making it accessible on the host network
- For production deployments, consider:
  - Adding authentication to Ollama
  - Using a reverse proxy with authentication
  - Restricting network access with firewall rules

## Expected Artifacts for Bug Reports

If you encounter issues, collect these artifacts for troubleshooting:

1. Output of `docker ps`
2. Output of `docker logs willow --tail 200`
3. Output of `docker logs ollama --tail 200`
4. The Willow environment variables: `docker exec willow env | grep -i OLLAMA`

With these artifacts, support teams can identify the exact failing step without guessing.