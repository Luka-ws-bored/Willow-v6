import streamlit as st
import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add willow to path
sys.path.insert(0, str(Path(__file__).parent))

# Import database service
try:
    from database import db_service, ChatSession, ChatMessage
except ImportError as e:
    st.error(f"Failed to import database service: {e}")
    st.stop()

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

# Initialize session state with database integration
if 'session_id' not in st.session_state:
    # Create new chat session in database
    st.session_state.session_id = db_service.create_chat_session(
        provider="openrouter",
        plugins=["color_mood_mapper", "bug_buster", "sql_sorcerer", "prompt_checker"]
    )

if 'messages' not in st.session_state:
    # Load messages from database
    db_messages = db_service.get_session_messages(st.session_state.session_id)
    st.session_state.messages = [
        {"role": msg.role, "content": msg.content, "metadata": msg.message_metadata}
        for msg in db_messages
    ]

if 'provider' not in st.session_state:
    # Load provider from database or use default
    session = db_service.get_chat_session(st.session_state.session_id)
    st.session_state.provider = session.provider if session else "openrouter"

if 'plugins' not in st.session_state:
    # Load plugins from database or use default
    session = db_service.get_chat_session(st.session_state.session_id)
    st.session_state.plugins = session.active_plugins if session else ["color_mood_mapper", "bug_buster", "sql_sorcerer", "prompt_checker"]

if 'uploaded_docs' not in st.session_state:
    # Load uploaded documents from database
    db_docs = db_service.get_session_documents(st.session_state.session_id)
    st.session_state.uploaded_docs = [doc.filename for doc in db_docs]

# Main interface
st.title("🌿 Willow v6 Chat Interface")
st.markdown("*AI-powered assistant with multiple LLM providers and plugin system*")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Provider selection
    st.subheader("🔧 LLM Provider")
    providers = ["openrouter", "ollama", "gemini"]
    selected_provider = st.selectbox("Select Provider", providers, index=providers.index(st.session_state.provider) if st.session_state.provider in providers else 0)
    
    # Update provider in database if changed
    if selected_provider != st.session_state.provider:
        st.session_state.provider = selected_provider
        db_service.update_chat_session(st.session_state.session_id, provider=selected_provider)
    
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
    
    # Update plugins in database if changed
    if selected_plugins != st.session_state.plugins:
        st.session_state.plugins = selected_plugins
        db_service.update_chat_session(st.session_state.session_id, active_plugins=selected_plugins)
    
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
        
        new_files = []
        for file in uploaded_files:
            file_path = docs_dir / file.name
            if not file_path.exists():  # Only process new files
                file_path.write_bytes(file.getbuffer())
                
                # Save to database
                content_preview = file.getvalue().decode('utf-8', errors='ignore')[:500] if file.type.startswith('text/') else None
                db_service.save_uploaded_document(
                    session_id=st.session_state.session_id,
                    filename=file.name,
                    file_path=str(file_path),
                    content_preview=content_preview,
                    file_size=file.size,
                    content_type=file.type
                )
                new_files.append(file.name)
        
        if new_files:
            st.success(f"Uploaded {len(new_files)} new documents")
            # Refresh uploaded docs from database
            db_docs = db_service.get_session_documents(st.session_state.session_id)
            st.session_state.uploaded_docs = [doc.filename for doc in db_docs]
    
    if st.session_state.uploaded_docs:
        st.write("**Uploaded:**")
        for doc in st.session_state.uploaded_docs:
            st.write(f"• {doc}")
    
    # Actions
    st.subheader("⚡ Actions")
    if st.button("Clear Chat"):
        # Clear from database and session state
        db_service.clear_session_messages(st.session_state.session_id)
        st.session_state.messages = []
        st.success("Chat cleared!")
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
    
    # Database statistics
    st.subheader("📊 Database Stats")
    try:
        db_stats = db_service.get_database_stats()
        st.write(f"**Total Sessions:** {db_stats['total_sessions']}")
        st.write(f"**Active Sessions:** {db_stats['active_sessions']}")
        st.write(f"**Total Messages:** {db_stats['total_messages']}")
        st.write(f"**Documents:** {db_stats['total_documents']}")
        
        # Session message stats
        session_stats = db_service.get_message_stats(st.session_state.session_id)
        st.write(f"**This Session:** {session_stats['total_messages']} messages")
    except Exception as e:
        st.error(f"Database error: {e}")
    
    # Session management
    st.subheader("📝 Session Management")
    if st.button("New Chat Session"):
        # Create new session
        new_session_id = db_service.create_chat_session(
            provider=st.session_state.provider,
            plugins=st.session_state.plugins
        )
        st.session_state.session_id = new_session_id
        st.session_state.messages = []
        st.success("New chat session created!")
        st.rerun()
    
    # Recent sessions
    try:
        recent_sessions = db_service.get_recent_sessions(5)
        if recent_sessions:
            st.write("**Recent Sessions:**")
            for session in recent_sessions:
                session_name = f"Session ({session.provider}) - {session.updated_at.strftime('%m/%d %H:%M')}"
                if st.button(session_name, key=f"session_{session.id}"):
                    st.session_state.session_id = session.id
                    # Load session data
                    db_messages = db_service.get_session_messages(session.id)
                    st.session_state.messages = [
                        {"role": msg.role, "content": msg.content, "metadata": msg.message_metadata}
                        for msg in db_messages
                    ]
                    st.session_state.provider = session.provider
                    st.session_state.plugins = session.active_plugins
                    st.rerun()
    except Exception as e:
        st.error(f"Error loading sessions: {e}")

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
    # Save user message to database
    user_metadata = {"provider": st.session_state.provider, "timestamp": datetime.now().isoformat()}
    db_service.save_message(
        session_id=st.session_state.session_id,
        role="user",
        content=prompt,
        message_metadata=user_metadata,
        provider=st.session_state.provider,
        plugins=st.session_state.plugins
    )
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt, "metadata": user_metadata})
    
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
            
            # Save assistant message to database
            assistant_metadata = {
                "provider": st.session_state.provider,
                "plugins_used": st.session_state.plugins,
                "enhanced_prompt_used": enhanced_prompt != prompt,
                "timestamp": datetime.now().isoformat()
            }
            db_service.save_message(
                session_id=st.session_state.session_id,
                role="assistant",
                content=response,
                message_metadata=assistant_metadata,
                provider=st.session_state.provider,
                plugins=st.session_state.plugins
            )
            
            # Add to session state
            st.session_state.messages.append({"role": "assistant", "content": response, "metadata": assistant_metadata})

# Footer
st.divider()
st.markdown("*Powered by Willow v6 Framework*")

# Export functionality
if st.session_state.messages:
    col1, col2 = st.columns(2)
    
    with col1:
        # Export session data from database
        try:
            session_data = db_service.export_session_data(st.session_state.session_id)
            st.download_button(
                "📥 Export Full Session",
                json.dumps(session_data, indent=2),
                f"willow_session_{st.session_state.session_id[:8]}.json",
                "application/json",
                help="Export complete session data including metadata"
            )
        except Exception as e:
            st.error(f"Export error: {e}")
    
    with col2:
        # Simple chat export
        simple_chat = {
            "messages": st.session_state.messages,
            "provider": st.session_state.provider,
            "plugins": st.session_state.plugins,
            "exported_at": datetime.now().isoformat()
        }
        st.download_button(
            "📤 Export Chat Only",
            json.dumps(simple_chat, indent=2),
            "willow_chat.json",
            "application/json",
            help="Export just the chat messages"
        )