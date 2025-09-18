from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import re
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    
    # Placeholder RAG response
    rag_response = f"Willow received: {user_message}"
    
    return jsonify({"response": rag_response})

@app.route('/ingest', methods=['POST'])
def ingest_document():
    """Handle document ingestion from n8n workflows."""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate input
        if not data:
            logger.error("No JSON data received in /ingest endpoint")
            return jsonify({"error": "No JSON data received"}), 400
        
        document = data.get("document")
        if not document:
            logger.error("No document field in request to /ingest endpoint")
            return jsonify({"error": "Missing 'document' field in request"}), 400
        
        if not isinstance(document, str):
            logger.error(f"Document field is not a string in /ingest endpoint: {type(document)}")
            return jsonify({"error": "'document' field must be a string"}), 400
        
        # Additional validation: check if document is empty or only whitespace
        if not document.strip():
            logger.error("Document field is empty or only whitespace in /ingest endpoint")
            return jsonify({"error": "Document field cannot be empty"}), 400
        
        # Sanitize input (limit length to prevent abuse)
        max_length = 100000  # 100KB limit
        if len(document) > max_length:
            logger.warning(f"Document truncated from {len(document)} to {max_length} characters in /ingest endpoint")
            document = document[:max_length]
        
        # Further sanitize by removing any null bytes or control characters
        document = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', document)
        
        # Import vector database functionality
        try:
            from src.utils.vector_db import VectorDB
        except ImportError:
            try:
                from src.vector_db import VectorDB
            except ImportError:
                try:
                    # Try alternative import path
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
                    from utils.vector_db import VectorDB
                except ImportError:
                    logger.error("Could not import VectorDB module in /ingest endpoint")
                    return jsonify({"error": "Vector database module not available"}), 500
        
        # Process document with vector database
        try:
            # Initialize vector database
            db = VectorDB()
            
            # Add document to vector database
            db.add_documents([document])
            
            logger.info(f"Successfully ingested document of length {len(document)} characters via /ingest endpoint")
            return jsonify({"status": "success", "message": "Document ingested successfully"}), 200
            
        except Exception as e:
            logger.error(f"Error processing document in /ingest endpoint: {str(e)}")
            return jsonify({"error": f"Error processing document: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in ingest endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the service is running."""
    return jsonify({
        "status": "healthy",
        "service": "Willow Backend",
        "version": "1.0"
    })

@app.route('/llm/status', methods=['GET'])
def llm_status():
    """Check the status of the LLM connection."""
    ollama_url = os.getenv("OLLAMA_API_URL", "http://ollama:11434")
    
    try:
        # Try to connect to the Ollama API
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "connected": True,
                "backend": "ollama",
                "url": ollama_url,
                "models": response.json() if response.content else []
            })
        else:
            return jsonify({
                "connected": False,
                "backend": "ollama",
                "url": ollama_url,
                "error": f"Status code: {response.status_code}"
            })
    except requests.exceptions.ConnectionError as e:
        return jsonify({
            "connected": False,
            "backend": "ollama",
            "url": ollama_url,
            "error": f"Connection error: {str(e)}"
        })
    except Exception as e:
        return jsonify({
            "connected": False,
            "backend": "ollama",
            "url": ollama_url,
            "error": f"Unexpected error: {str(e)}"
        })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)