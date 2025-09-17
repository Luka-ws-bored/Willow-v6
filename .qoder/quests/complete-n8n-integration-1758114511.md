# Complete n8n Integration for Willow Document Ingestion - Design Document

## 1. Overview

This document outlines the design for completing the n8n integration with Willow to automate document ingestion workflows. The integration will allow users to trigger document ingestion processes through n8n workflows, which will communicate with Willow's Python backend to process and store documents in the vector database.

## 2. Architecture

The integration consists of three main components:

1. **n8n Service**: Docker container running n8n with a predefined workflow
2. **Willow Python Backend**: Flask application with an `/ingest` endpoint
3. **Vector Database**: FAISS-based vector storage for document embeddings

Architecture flow: External Trigger → n8n Webhook → Data Processing → HTTP Request to Willow → Willow Backend /ingest → Vector Database → Response → n8n Webhook

## 3. Component Design

### 3.1 n8n Configuration

#### Directory Structure

Directory structure:
- devops/n8n/
  - docker-compose.yml
  - .env.example
  - README.md
  - n8n_data/
  - workflows/
    - willow_document_ingest.json

#### Docker Compose Configuration

The `docker-compose.yml` defines the n8n service with:

- Port mapping (5678:5678)
- Basic authentication using environment variables
- SQLite database for persistence
- Volume mapping for data persistence

#### Environment Configuration

The `.env.example` file provides placeholders for:

- `N8N_USER`: n8n admin username
- `N8N_PASS`: n8n admin password

### 3.2 n8n Workflow

The workflow JSON defines a three-node process:

1. **Webhook Node**: Listens for POST requests at `/ingest`
2. **Extract Text Node**: Processes incoming data (pass-through function)
3. **HTTP Request Node**: Calls the Willow backend at `http://localhost:5000/ingest`

### 3.3 Python Backend Endpoint

#### Endpoint: `/ingest`

- **Method**: POST
- **Input**: JSON with `document` field
- **Process**:
  1. Validate input data
  2. Extract and sanitize document text
  3. Process document with vector database
  4. Return success/failure response

#### Input Validation

- Check for JSON payload
- Verify `document` field exists
- Ensure `document` is a string
- Limit document length to prevent abuse

#### Vector Database Integration

- Import VectorDB module
- Initialize vector database
- Add document to vector database
- Handle exceptions during processing

### 3.4 Vector Database Integration

The integration uses the existing `VectorDB` class from `src/utils/vector_db.py`:

- `add_documents()` method to store document embeddings
- Error handling for import and processing failures
- Logging for successful operations and errors

## 4. API Endpoints Reference

### 4.1 n8n Webhook

- **URL**: `http://localhost:5678/webhook/ingest`
- **Method**: POST
- **Body**:
JSON with document field containing the content to ingest

### 4.2 Willow Backend Ingest

- **URL**: `http://localhost:5000/ingest`
- **Method**: POST
- **Body**:
JSON with document field containing the content to ingest
- **Responses**:
  - 200: Success
  - 400: Invalid input
  - 500: Processing error

## 5. Data Models

### 5.1 Document Model

Document: string (required)

### 5.2 Response Models

Success response:
Status: success
Message: Document ingested successfully

Error response:
Error: Error description

## 6. Business Logic Layer

### 6.1 Document Ingestion Flow

1. Receive document via n8n webhook
2. Process through n8n workflow
3. Forward to Willow backend
4. Validate input in backend
5. Sanitize document content
6. Generate embeddings using SentenceTransformer
7. Store embeddings in FAISS index
8. Return status to n8n

### 6.2 Error Handling

- Input validation errors (400)
- Processing errors (500)
- Import errors for VectorDB module
- Logging for all error conditions

## 7. Security Considerations

- Basic authentication for n8n UI
- Input validation and sanitization
- Environment variable management
- Document length limits to prevent abuse
- Secure credential storage guidelines

## 8. Testing

### 8.1 Unit Tests

- Input validation tests
- Error handling tests
- VectorDB integration tests

### 8.2 Integration Tests

- End-to-end workflow testing
- n8n to backend communication
- Document ingestion verification

### 8.3 Manual Testing

- Docker Compose setup
- n8n workflow import
- curl-based workflow testing

## 9. Deployment

### 9.1 Prerequisites

- Docker and Docker Compose
- Python backend running on port 5000
- Required Python dependencies installed

### 9.2 Setup Steps

1. Configure environment variables
2. Start n8n with Docker Compose
3. Start Willow backend
4. Import workflow in n8n UI
5. Test with curl command

## 10. Monitoring and Logging

- Backend logging for ingestion operations
- Error logging for failed operations
- n8n workflow execution logs
- Vector database operation metrics
