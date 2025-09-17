# n8n Integration for Willow Document Ingestion

This integration allows you to automate document ingestion workflows using n8n with Willow's vector database.

## Prerequisites

- Docker and Docker Compose installed
- Python backend running (Willow)
- n8n Docker image available

## Setup Instructions

### 1. Configure Environment Variables

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and update the credentials:
   ```bash
   N8N_USER=your_username
   N8N_PASS=your_secure_password
   ```

### 2. Start n8n

From the `devops/n8n` directory, run:

```bash
docker-compose up -d
```

This will start n8n on port 5678. You can access the n8n UI at http://localhost:5678

### 3. Start Willow Backend

Make sure the Willow Python backend is running:

```bash
python backend.py
```

This should start the backend on port 5000.

### 4. Import Workflow

1. Access the n8n UI at http://localhost:5678
2. Log in with your credentials
3. Click on "Workflows" in the left sidebar
4. Click "Import"
5. Select the `workflows/willow_document_ingest.json` file
6. Click "Import"

## Testing the Integration

### Using curl

You can test the end-to-end workflow with curl:

```bash
curl -X POST http://localhost:5678/webhook/ingest \
  -H "Content-Type: application/json" \
  -d '{"document": "This is a test document for ingestion into Willow."}'
```

### Using the test scripts

The project includes several test scripts:

1. **test_n8n_curl.sh** - Bash script for testing with curl
2. **test_n8n_curl.bat** - Windows batch script for testing with curl
3. **test_n8n_full_integration.py** - Comprehensive Python test suite

Run the Python test suite:
```bash
python test_n8n_full_integration.py
```

### Expected Response

If successful, you should receive a response like:

```json
{
  "status": "success",
  "message": "Document ingested successfully"
}
```

## Workflow Details

The n8n workflow consists of three nodes:

1. **Webhook**: Listens for POST requests at `/ingest`
2. **Extract Text**: Processes the incoming data (pass-through in this basic version)
3. **Call Python Ingest**: Makes an HTTP request to the Willow backend at `http://localhost:5000/ingest`

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure both n8n and Willow backend are running
2. **Authentication Failed**: Check your `.env` credentials
3. **Document Not Ingested**: Check the Willow backend logs for errors
4. **Vector DB Errors**: Ensure FAISS and sentence-transformers are installed

### Logs

- n8n logs: `docker-compose logs -f`
- Willow backend logs: Check the terminal where you started `backend.py`

## Security Notes

- Always use strong passwords in production
- Never commit `.env` files to version control
- Consider adding additional authentication for the `/ingest` endpoint in production
- Document length is limited to prevent abuse (100KB max)