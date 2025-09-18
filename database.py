"""
Database service for Willow v6 Chat Interface
Provides persistent storage for chat messages, user sessions, and document metadata.
"""

import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    provider = Column(String, nullable=False)
    active_plugins = Column(JSON, default=list)
    rag_settings = Column(JSON, default=dict)
    session_name = Column(String, default="Chat Session")
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    provider_used = Column(String)
    plugins_active = Column(JSON, default=list)

class UploadedDocument(Base):
    """Uploaded document model"""
    __tablename__ = "uploaded_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    content_preview = Column(Text)
    file_size = Column(Integer)
    content_type = Column(String)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_for_rag = Column(Boolean, default=False)

class UserPreference(Base):
    """User preferences model"""
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False)
    preference_key = Column(String, nullable=False)
    preference_value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DatabaseService:
    """Database service for Willow Chat Interface"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.create_tables()
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # Chat Session Methods
    def create_chat_session(self, provider: str, plugins: List[str] = None, rag_settings: Dict = None) -> str:
        """Create a new chat session"""
        with self.get_session() as db:
            session = ChatSession(
                provider=provider,
                active_plugins=plugins or [],
                rag_settings=rag_settings or {}
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session.id
    
    def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        with self.get_session() as db:
            return db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    def update_chat_session(self, session_id: str, **kwargs):
        """Update chat session"""
        with self.get_session() as db:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                session.updated_at = datetime.now(timezone.utc)
                db.commit()
    
    def get_recent_sessions(self, limit: int = 10) -> List[ChatSession]:
        """Get recent chat sessions"""
        with self.get_session() as db:
            return db.query(ChatSession).filter(ChatSession.is_active == True)\
                     .order_by(ChatSession.updated_at.desc()).limit(limit).all()
    
    # Chat Message Methods
    def save_message(self, session_id: str, role: str, content: str, 
                    message_metadata: Dict = None, provider: str = None, plugins: List[str] = None) -> str:
        """Save a chat message"""
        with self.get_session() as db:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                message_metadata=message_metadata or {},
                provider_used=provider,
                plugins_active=plugins or []
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message.id
    
    def get_session_messages(self, session_id: str, limit: int = 100) -> List[ChatMessage]:
        """Get messages for a session"""
        with self.get_session() as db:
            return db.query(ChatMessage).filter(ChatMessage.session_id == session_id)\
                     .order_by(ChatMessage.timestamp.asc()).limit(limit).all()
    
    def clear_session_messages(self, session_id: str):
        """Clear all messages for a session"""
        with self.get_session() as db:
            db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
            db.commit()
    
    def get_message_stats(self, session_id: str) -> Dict[str, Any]:
        """Get message statistics for a session"""
        with self.get_session() as db:
            messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
            
            stats = {
                "total_messages": len(messages),
                "user_messages": len([m for m in messages if m.role == "user"]),
                "assistant_messages": len([m for m in messages if m.role == "assistant"]),
                "providers_used": list(set([m.provider_used for m in messages if m.provider_used])),
                "first_message": messages[0].timestamp if messages else None,
                "last_message": messages[-1].timestamp if messages else None
            }
            return stats
    
    # Document Methods
    def save_uploaded_document(self, session_id: str, filename: str, file_path: str,
                             content_preview: str = None, file_size: int = None,
                             content_type: str = None) -> str:
        """Save uploaded document metadata"""
        with self.get_session() as db:
            document = UploadedDocument(
                session_id=session_id,
                filename=filename,
                file_path=file_path,
                content_preview=content_preview,
                file_size=file_size,
                content_type=content_type
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            return document.id
    
    def get_session_documents(self, session_id: str) -> List[UploadedDocument]:
        """Get documents for a session"""
        with self.get_session() as db:
            return db.query(UploadedDocument).filter(UploadedDocument.session_id == session_id)\
                     .order_by(UploadedDocument.uploaded_at.desc()).all()
    
    def mark_document_processed(self, document_id: str):
        """Mark document as processed for RAG"""
        with self.get_session() as db:
            document = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
            if document:
                document.processed_for_rag = True
                db.commit()
    
    # User Preferences Methods
    def save_preference(self, session_id: str, key: str, value: Any):
        """Save user preference"""
        with self.get_session() as db:
            # Check if preference exists
            pref = db.query(UserPreference).filter(
                UserPreference.session_id == session_id,
                UserPreference.preference_key == key
            ).first()
            
            if pref:
                pref.preference_value = value
                pref.updated_at = datetime.now(timezone.utc)
            else:
                pref = UserPreference(
                    session_id=session_id,
                    preference_key=key,
                    preference_value=value
                )
                db.add(pref)
            
            db.commit()
    
    def get_preference(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get user preference"""
        with self.get_session() as db:
            pref = db.query(UserPreference).filter(
                UserPreference.session_id == session_id,
                UserPreference.preference_key == key
            ).first()
            
            return pref.preference_value if pref else default
    
    def get_all_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get all preferences for a session"""
        with self.get_session() as db:
            prefs = db.query(UserPreference).filter(UserPreference.session_id == session_id).all()
            return {pref.preference_key: pref.preference_value for pref in prefs}
    
    # Utility Methods
    def export_session_data(self, session_id: str) -> Dict[str, Any]:
        """Export all session data"""
        session = self.get_chat_session(session_id)
        messages = self.get_session_messages(session_id)
        documents = self.get_session_documents(session_id)
        preferences = self.get_all_preferences(session_id)
        
        return {
            "session": {
                "id": session.id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "provider": session.provider,
                "active_plugins": session.active_plugins,
                "rag_settings": session.rag_settings,
                "session_name": session.session_name
            } if session else None,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.message_metadata,
                    "provider_used": msg.provider_used,
                    "plugins_active": msg.plugins_active
                }
                for msg in messages
            ],
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "file_path": doc.file_path,
                    "content_preview": doc.content_preview,
                    "file_size": doc.file_size,
                    "content_type": doc.content_type,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "processed_for_rag": doc.processed_for_rag
                }
                for doc in documents
            ],
            "preferences": preferences
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        with self.get_session() as db:
            return {
                "total_sessions": db.query(ChatSession).count(),
                "active_sessions": db.query(ChatSession).filter(ChatSession.is_active == True).count(),
                "total_messages": db.query(ChatMessage).count(),
                "total_documents": db.query(UploadedDocument).count(),
                "processed_documents": db.query(UploadedDocument).filter(UploadedDocument.processed_for_rag == True).count()
            }

# Global database service instance
db_service = DatabaseService()