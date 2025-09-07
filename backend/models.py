"""
Database models for GLTR Webtoon Platform (Updated for Text2Cuts)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Webtoon(Base):
    __tablename__ = 'webtoons'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text)  # 추가: 스토리 요약
    description = Column(Text)
    thumbnail_url = Column(String(500))
    author_name = Column(String(100), default='Anonymous')
    genre = Column(String(50))
    theme = Column(String(100))
    story_style = Column(String(100))
    number_of_cuts = Column(Integer)  # 추가: 컷 수
    status = Column(String(20), default='published')
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    session_id = Column(String(100))  # 브라우저 세션으로 소유권 확인
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scenes = relationship("Scene", back_populates="webtoon", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="webtoon", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="webtoon", cascade="all, delete-orphan")
    generation_sessions = relationship("GenerationSession", back_populates="webtoon")
    images = relationship("ImageAsset", back_populates="webtoon")
    likes = relationship("Like", back_populates="webtoon", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="webtoon", cascade="all, delete-orphan")


class Scene(Base):
    __tablename__ = 'scenes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    webtoon_id = Column(UUID(as_uuid=True), ForeignKey('webtoons.id', ondelete='CASCADE'))
    scene_number = Column(Integer, nullable=False)
    scene_description = Column(Text)
    image_url = Column(String(500))
    narration = Column(Text)
    character_positions = Column(JSON)
    panel_layout = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="scenes")
    dialogues = relationship("Dialogue", back_populates="scene", cascade="all, delete-orphan")
    edit_history = relationship("EditHistory", back_populates="scene", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="scene", cascade="all, delete-orphan")
    images = relationship("ImageAsset", back_populates="scene")
    chat_messages = relationship("ChatMessage", back_populates="scene")
    
    __table_args__ = (
        UniqueConstraint('webtoon_id', 'scene_number'),
        Index('idx_scenes_order', 'webtoon_id', 'scene_number'),
    )


class Dialogue(Base):
    __tablename__ = 'dialogues'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scene_id = Column(UUID(as_uuid=True), ForeignKey('scenes.id', ondelete='CASCADE'))
    who_speaks = Column(String(100), nullable=False)
    dialogue = Column(Text, nullable=False)
    fact_or_fiction = Column(String(20), default='fiction')
    dialogue_order = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scene = relationship("Scene", back_populates="dialogues")
    
    __table_args__ = (
        UniqueConstraint('scene_id', 'dialogue_order'),
        Index('idx_dialogues_order', 'scene_id', 'dialogue_order'),
    )


class Character(Base):
    __tablename__ = 'characters'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    webtoon_id = Column(UUID(as_uuid=True), ForeignKey('webtoons.id', ondelete='CASCADE'))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    appearance = Column(Text)
    personality = Column(Text)
    role = Column(String(50))
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="characters")
    chat_messages = relationship("ChatMessage", back_populates="character")


class EditHistory(Base):
    __tablename__ = 'edit_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scene_id = Column(UUID(as_uuid=True), ForeignKey('scenes.id', ondelete='CASCADE'))
    session_id = Column(String(100))
    edit_type = Column(String(50))
    original_content = Column(JSON)
    edited_content = Column(JSON)
    edit_command = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scene = relationship("Scene", back_populates="edit_history")


class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    webtoon_id = Column(UUID(as_uuid=True), ForeignKey('webtoons.id', ondelete='CASCADE'))
    scene_id = Column(Integer, ForeignKey('scenes.id', ondelete='CASCADE'), nullable=True)
    author_name = Column(String(100), default='익명')
    content = Column(Text, nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="comments")
    scene = relationship("Scene", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])


class GenerationSession(Base):
    __tablename__ = 'generation_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id'), nullable=True)
    input_text = Column(Text)
    generation_result = Column(JSON)  # 추가: 생성된 전체 JSON 결과 저장
    summary = Column(Text)
    theme = Column(String(200))
    story_style = Column(String(100))
    story_title = Column(String(200))  # 추가: 생성된 스토리 제목
    number_of_cuts = Column(Integer)  # 추가: 생성된 컷 수
    original_language = Column(String(10))
    llm_model = Column(String(50))
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="generation_sessions")


class ImageAsset(Base):
    __tablename__ = 'image_assets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(50))
    width = Column(Integer)
    height = Column(Integer)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id'), nullable=True)
    scene_id = Column(UUID(as_uuid=True), ForeignKey('scenes.id'), nullable=True)
    asset_type = Column(String(50))
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="images")
    scene = relationship("Scene", back_populates="images")


class Like(Base):
    __tablename__ = 'likes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    webtoon_id = Column(UUID(as_uuid=True), ForeignKey('webtoons.id', ondelete='CASCADE'))
    session_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="likes")
    
    __table_args__ = (
        UniqueConstraint('webtoon_id', 'session_id'),
    )


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    webtoon_id = Column(UUID(as_uuid=True), ForeignKey('webtoons.id', ondelete='CASCADE'))
    scene_id = Column(UUID(as_uuid=True), ForeignKey('scenes.id'), nullable=True)
    sender_type = Column(String(20), nullable=False)  # 'user' or 'character'
    sender_name = Column(String(100))
    message = Column(Text, nullable=False)
    session_id = Column(String(100))
    is_read = Column(Boolean, default=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=True)
    parent_message_id = Column(UUID(as_uuid=True), ForeignKey('chat_messages.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship("Webtoon", back_populates="chat_messages")
    scene = relationship("Scene", back_populates="chat_messages")
    character = relationship("Character", back_populates="chat_messages")
    replies = relationship("ChatMessage", backref="parent", remote_side=[id])