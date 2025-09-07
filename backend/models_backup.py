"""
Database models for GLTR Webtoon Platform (No Auth Version)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Webtoon(Base):
    __tablename__ = 'webtoons'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    thumbnail_url = Column(String(500))
    author_name = Column(String(100), default='Anonymous')
    genre = Column(String(50))
    theme = Column(String(100))
    story_style = Column(String(100))
    status = Column(String(20), default='published')
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    session_id = Column(String(100))  # 브라우저 세션으로 소유권 확인
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    episodes = relationship("Episode", back_populates="webtoon", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="webtoon", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="webtoon", cascade="all, delete-orphan")
    generation_sessions = relationship("GenerationSession", back_populates="webtoon")
    images = relationship("ImageAsset", back_populates="webtoon")
    likes = relationship("Like", back_populates="webtoon", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = 'episodes'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id', ondelete='CASCADE'))
    episode_number = Column(Integer, nullable=False)
    title = Column(String(200))
    scene_order = Column(Integer, nullable=False)
    image_url = Column(String(500))
    dialogue = Column(Text)
    description = Column(Text)
    narration = Column(Text)
    character_positions = Column(JSON)
    panel_layout = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="episodes")
    edit_history = relationship("EditHistory", back_populates="episode", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="episode", cascade="all, delete-orphan")
    images = relationship("ImageAsset", back_populates="episode")
    
    __table_args__ = (
        UniqueConstraint('webtoon_id', 'episode_number', 'scene_order'),
        Index('idx_episodes_order', 'webtoon_id', 'episode_number', 'scene_order'),
    )


class Character(Base):
    __tablename__ = 'characters'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id', ondelete='CASCADE'))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    appearance = Column(Text)
    personality = Column(Text)
    role = Column(String(50))
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="characters")


class EditHistory(Base):
    __tablename__ = 'edit_history'
    
    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey('episodes.id', ondelete='CASCADE'))
    session_id = Column(String(100))
    edit_type = Column(String(50))
    original_content = Column(JSON)
    edited_content = Column(JSON)
    edit_command = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    episode = relationship("Episode", back_populates="edit_history")


class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id', ondelete='CASCADE'))
    episode_id = Column(Integer, ForeignKey('episodes.id', ondelete='CASCADE'), nullable=True)
    author_name = Column(String(100), default='익명')
    content = Column(Text, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="comments")
    episode = relationship("Episode", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])


class GenerationSession(Base):
    __tablename__ = 'generation_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id'), nullable=True)
    input_text = Column(Text)
    summary = Column(Text)
    theme = Column(String(200))
    story_style = Column(String(100))
    original_language = Column(String(10))
    llm_model = Column(String(50))
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="generation_sessions")


class ImageAsset(Base):
    __tablename__ = 'image_assets'
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(50))
    width = Column(Integer)
    height = Column(Integer)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id'), nullable=True)
    episode_id = Column(Integer, ForeignKey('episodes.id'), nullable=True)
    asset_type = Column(String(50))
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="images")
    episode = relationship("Episode", back_populates="images")


class Like(Base):
    __tablename__ = 'likes'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id', ondelete='CASCADE'))
    session_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="likes")
    
    __table_args__ = (
        UniqueConstraint('webtoon_id', 'session_id'),
    )


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id', ondelete='CASCADE'))
    episode_id = Column(Integer, ForeignKey('episodes.id'), nullable=True)
    sender_type = Column(String(20), nullable=False)  # 'user' or 'character'
    sender_name = Column(String(100))
    message = Column(Text, nullable=False)
    session_id = Column(String(100))
    is_read = Column(Boolean, default=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    parent_message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", backref="chat_messages")
    episode = relationship("Episode", backref="chat_messages")
    character = relationship("Character", backref="chat_messages")
    replies = relationship("ChatMessage", backref="parent", remote_side=[id])
