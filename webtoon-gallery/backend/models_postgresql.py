from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Table, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_postgresql import Base
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import enum

webtoon_genre_association = Table(
    'webtoon_genres',
    Base.metadata,
    Column('webtoon_id', Integer, ForeignKey('webtoons.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

webtoon_tag_association = Table(
    'webtoon_tags',
    Base.metadata,
    Column('webtoon_id', Integer, ForeignKey('webtoons.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class StatusEnum(str, enum.Enum):
    ongoing = "ongoing"
    completed = "completed"
    hiatus = "hiatus"

class ImageTypeEnum(str, enum.Enum):
    THUMBNAIL = "thumbnail"
    EPISODE = "episode"
    CHARACTER = "character"
    BACKGROUND = "background"

class Genre(Base):
    __tablename__ = 'genres'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    webtoons = relationship("Webtoon", secondary=webtoon_genre_association, back_populates="genres")

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    webtoons = relationship("Webtoon", secondary=webtoon_tag_association, back_populates="tags")

class Webtoon(Base):
    __tablename__ = 'webtoons'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    author = Column(String(100))
    thumbnail = Column(String(500))
    total_episodes = Column(Integer, default=0)
    world_setting = Column(Text)
    main_prompt = Column(Text)
    style_prompt = Column(Text)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.ongoing)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    genres = relationship("Genre", secondary=webtoon_genre_association, back_populates="webtoons")
    tags = relationship("Tag", secondary=webtoon_tag_association, back_populates="webtoons")
    episodes = relationship("Episode", back_populates="webtoon", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="webtoon", cascade="all, delete-orphan")
    images = relationship("WebtoonImage", back_populates="webtoon", cascade="all, delete-orphan")

class Episode(Base):
    __tablename__ = 'episodes'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id'))
    episode_number = Column(Integer)
    title = Column(String(200))
    images = Column(JSON)  # List of image URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    webtoon = relationship("Webtoon", back_populates="episodes")
    storyboard_panels = relationship("StoryboardPanel", back_populates="episode", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = 'characters'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id'))
    name = Column(String(100))
    description = Column(Text)
    design_prompt = Column(Text)
    reference_images = Column(JSON)  # List of image URLs
    
    webtoon = relationship("Webtoon", back_populates="characters")

class WebtoonImage(Base):
    __tablename__ = 'webtoon_images'
    
    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id'))
    url = Column(String(500))
    type = Column(SQLEnum(ImageTypeEnum))
    episode = Column(Integer, nullable=True)
    panel_number = Column(Integer, nullable=True)
    generation_prompt = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    webtoon = relationship("Webtoon", back_populates="images")

class StoryboardPanel(Base):
    __tablename__ = 'storyboard_panels'
    
    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey('episodes.id'))
    panel_number = Column(Integer)
    description = Column(Text)
    dialogue = Column(Text, nullable=True)
    camera_angle = Column(String(100))
    scene_prompt = Column(Text)
    
    episode = relationship("Episode", back_populates="storyboard_panels")

# Pydantic models for API
class WebtoonBase(BaseModel):
    title: str
    description: Optional[str] = None
    genre: List[str] = []
    author: Optional[str] = None
    thumbnail: Optional[str] = None

class WebtoonCreate(WebtoonBase):
    world_setting: Optional[str] = None
    main_prompt: Optional[str] = None
    style_prompt: Optional[str] = None
    tags: List[str] = []
    status: str = "ongoing"

class WebtoonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[List[str]] = None
    author: Optional[str] = None
    thumbnail: Optional[str] = None
    world_setting: Optional[str] = None
    main_prompt: Optional[str] = None
    style_prompt: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class WebtoonEdit(BaseModel):
    drawing: Optional[dict] = None
    llm_question: Optional[str] = None

class WebtoonResponse(WebtoonBase):
    id: int
    episodes: List[dict] = []
    total_episodes: int = 0
    characters: List[dict] = []
    all_images: List[dict] = []
    tags: List[str] = []
    status: str = "ongoing"
    created_at: datetime
    updated_at: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0

    class Config:
        from_attributes = True

class PaginatedWebtoons(BaseModel):
    items: List[WebtoonResponse]
    total: int
    page: int
    per_page: int
    has_more: bool