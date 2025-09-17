from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    
    # Placeholder RAG response
    rag_response = f"Willow received: {user_message}"
    
    return jsonify({"response": rag_response})

if __name__ == "__main__":
    app.run(port=5000)