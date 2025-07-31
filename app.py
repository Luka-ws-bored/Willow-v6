import streamlit as st
import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add willow to path
sys.path.insert(0, str(Path(__file__).parent))

class LLMProviders:
    """Integrated LLM providers for Willow v6"""
    
    @staticmethod
    def openrouter(prompt, model="anthropic/claude-3-haiku"):
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            return "Please add your OpenRouter API key in the sidebar to continue."
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "HTTP-Referer": "https://willow-chat.local",
                    "X-Title": "Willow v6"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"API error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Connection error: {str(e)}"
    
    @staticmethod
    def ollama(prompt, model="llama3.1:8b"):
        url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        try:
            response = requests.post(
                f"{url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response from Ollama")
            else:
                return f"Ollama error {response.status_code}: {response.text}"
        except requests.exceptions.ConnectionError:
            return "Ollama not running. Start with: ollama serve"
        except Exception as e:
            return f"Ollama connection error: {str(e)}"
    
    @staticmethod
    def gemini(prompt):
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            return "Please add your Gemini API key in the sidebar."
        
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and data["candidates"]:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                return "No response from Gemini"
            else:
                return f"Gemini error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Gemini connection error: {str(e)}"

def enhance_prompt(prompt, plugins):
    """Add context based on active plugins"""
    context = ""
    
    if "color_mood_mapper" in plugins and any(word in prompt.lower() for word in ["color", "mood", "emotion"]):
        context += "Context: You're a color-mood expert. Help map colors to emotions. "
    
    if "bug_buster" in plugins and any(word in prompt.lower() for word in ["debug", "error", "bug", "fix", "code"]):
        context += "Context: You're a debugging expert. Help identify and fix issues. "
    
    if "sql_sorcerer" in plugins and any(word in prompt.lower() for word in ["sql", "database", "query"]):
        context += "Context: You're a SQL expert. Help with database queries. "
    
    if "prompt_checker" in plugins and any(word in prompt.lower() for word in ["prompt", "improve", "optimize"]):
        context += "Context: You're a prompt engineering expert. Optimize prompts. "
    
    return f"{context}{prompt}" if context else prompt

# Configure Streamlit
st.set_page_config(
    page_title="Willow v6 Chat",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'provider' not in st.session_state:
    st.session_state.provider = "openrouter"
if 'plugins' not in st.session_state:
    st.session_state.plugins = ["color_mood_mapper", "bug_buster", "sql_sorcerer", "prompt_checker"]
if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []

# Main interface
st.title("🌿 Willow v6 Chat Interface")
st.markdown("*AI-powered assistant with multiple LLM providers and plugin system*")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Provider selection
    st.subheader("🔧 LLM Provider")
    providers = ["openrouter", "ollama", "gemini"]
    st.session_state.provider = st.selectbox("Select Provider", providers)
    
    # API Keys
    st.subheader("🔑 API Keys")
    
    if st.session_state.provider == "openrouter":
        openrouter_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            value=os.getenv("OPENROUTER_API_KEY", ""),
            help="Get your key from openrouter.ai"
        )
        if openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = openrouter_key
        
        model = st.selectbox("Model", [
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
            "openai/gpt-4o",
            "openai/gpt-3.5-turbo",
            "meta-llama/llama-3.1-8b-instruct"
        ])
    
    elif st.session_state.provider == "gemini":
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Get your key from Google AI Studio"
        )
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
    
    elif st.session_state.provider == "ollama":
        ollama_url = st.text_input(
            "Ollama URL",
            value=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            help="Local Ollama server URL"
        )
        os.environ["OLLAMA_URL"] = ollama_url
        
        ollama_model = st.selectbox("Model", [
            "llama3.1:8b",
            "llama3:8b", 
            "mistral:7b",
            "codellama:7b"
        ])
    
    # Plugin management
    st.subheader("🔌 Plugins")
    available_plugins = ["color_mood_mapper", "bug_buster", "sql_sorcerer", "prompt_checker"]
    selected_plugins = []
    
    for plugin in available_plugins:
        if st.checkbox(
            plugin.replace("_", " ").title(),
            value=plugin in st.session_state.plugins
        ):
            selected_plugins.append(plugin)
    
    st.session_state.plugins = selected_plugins
    
    # Document upload
    st.subheader("📚 Documents")
    uploaded_files = st.file_uploader(
        "Upload for RAG",
        accept_multiple_files=True,
        type=['txt', 'md', 'pdf']
    )
    
    if uploaded_files:
        docs_dir = Path("uploaded_docs")
        docs_dir.mkdir(exist_ok=True)
        
        for file in uploaded_files:
            (docs_dir / file.name).write_bytes(file.getbuffer())
        
        st.success(f"Uploaded {len(uploaded_files)} documents")
        st.session_state.uploaded_docs = [f.name for f in uploaded_files]
    
    if st.session_state.uploaded_docs:
        st.write("**Uploaded:**")
        for doc in st.session_state.uploaded_docs:
            st.write(f"• {doc}")
    
    # Actions
    st.subheader("⚡ Actions")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Test Connection"):
        if st.session_state.provider == "openrouter":
            result = LLMProviders.openrouter("Hello", model if 'model' in locals() else "anthropic/claude-3-haiku")
        elif st.session_state.provider == "ollama":
            result = LLMProviders.ollama("Hello", ollama_model if 'ollama_model' in locals() else "llama3.1:8b")
        else:
            result = LLMProviders.gemini("Hello")
        
        if "error" in result.lower() or "not running" in result.lower():
            st.error("Connection failed")
        else:
            st.success("Connection works!")

# Stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Messages", len(st.session_state.messages))
with col2:
    st.metric("Plugins", len(st.session_state.plugins))
with col3:
    st.metric("Provider", st.session_state.provider.title())

st.divider()

# Chat interface
st.header("💬 Chat")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Message Willow..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Enhance prompt with plugin context
            enhanced_prompt = enhance_prompt(prompt, st.session_state.plugins)
            
            # Get response from selected provider
            if st.session_state.provider == "openrouter":
                response = LLMProviders.openrouter(
                    enhanced_prompt,
                    model if 'model' in locals() else "anthropic/claude-3-haiku"
                )
            elif st.session_state.provider == "ollama":
                response = LLMProviders.ollama(
                    enhanced_prompt,
                    ollama_model if 'ollama_model' in locals() else "llama3.1:8b"
                )
            else:
                response = LLMProviders.gemini(enhanced_prompt)
            
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.markdown("*Powered by Willow v6 Framework*")

# Export functionality
if st.session_state.messages:
    chat_data = {
        "messages": st.session_state.messages,
        "provider": st.session_state.provider,
        "plugins": st.session_state.plugins
    }
    st.download_button(
        "📥 Export Chat",
        json.dumps(chat_data, indent=2),
        "willow_chat.json",
        "application/json"
    )