# Willow v7 API Integration

## Overview

This document provides documentation for the API integration in the Willow v7 desktop application.

## Models API

The models API provides functionality for listing, selecting, and running AI models.

### Functions

#### `listModels()`

Retrieves a list of available AI models.

**Returns:** Promise<Array<{id, name, tps, context, status}>>

#### `setActiveModel(modelId)`

Sets the active AI model.

**Parameters:**
- `modelId` (string): ID of the model to activate

**Returns:** Promise<modelDetail>

#### `runChained(models, prompt)`

Runs a prompt through a chain of models.

**Parameters:**
- `models` (Array<string>): IDs of models to chain
- `prompt` (string): Prompt to process

**Returns:** Promise<response>

## RAG API

The RAG (Retrieval-Augmented Generation) API provides functionality for document ingestion and querying.

### Endpoints

#### `POST /api/ingest`

Ingests a document for RAG processing.

**Request Body:**
- `file` (File): Document to ingest

**Response:**
- `id` (string): ID of the ingested document
- `status` (string): Processing status

#### `GET /api/indexes`

Retrieves a list of document indexes.

**Response:** Array<{id, name, documentCount, lastUpdated}>

#### `GET /api/indexes/:id/docs`

Retrieves document chunks from an index.

**Parameters:**
- `id` (string): Index ID

**Response:** Array<{id, content, score}>

#### `POST /api/query`

Queries documents using RAG.

**Request Body:**
- `query` (string): Query to process

**Response:**
- `query` (string): Original query
- `results` (Array): Retrieved document chunks
- `response` (string): Generated response

## Implementation

The API integration is implemented in:
- `src/lib/api/models.js`
- `src/lib/api/rag.js`

These files currently contain mock implementations for development purposes. In a production environment, they would be replaced with actual API calls.