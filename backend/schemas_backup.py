"""
Pydantic schemas for API validation (No Auth Version)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class WebtoonStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"

class EditType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    LAYOUT = "layout"
    DIALOGUE = "dialogue"

# Webtoon schemas
class WebtoonBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    author_name: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)
    theme: Optional[str] = Field(None, max_length=100)
    story_style: Optional[str] = Field(None, max_length=100)

class WebtoonCreate(WebtoonBase):
    thumbnail_url: Optional[str] = None
    session_id: Optional[str] = None

class WebtoonUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    author_name: Optional[str] = Field(None, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)
    theme: Optional[str] = Field(None, max_length=100)
    story_style: Optional[str] = Field(None, max_length=100)
    status: Optional[WebtoonStatus] = None

class WebtoonInDB(WebtoonBase):
    id: int
    thumbnail_url: Optional[str]
    status: WebtoonStatus
    view_count: int
    like_count: int
    session_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WebtoonResponse(WebtoonInDB):
    is_owner: Optional[bool] = False
    is_liked: Optional[bool] = False

class WebtoonListResponse(BaseModel):
    webtoons: List[WebtoonResponse]
    total: int
    page: int
    per_page: int

# Episode schemas
class EpisodeBase(BaseModel):
    episode_number: int
    title: Optional[str] = Field(None, max_length=200)
    scene_order: int
    dialogue: Optional[str] = None
    description: Optional[str] = None
    narration: Optional[str] = None
    panel_layout: Optional[str] = Field(None, max_length=50)

class EpisodeCreate(EpisodeBase):
    webtoon_id: int
    image_url: Optional[str] = None
    character_positions: Optional[Dict[str, Any]] = None

class EpisodeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    dialogue: Optional[str] = None
    description: Optional[str] = None
    narration: Optional[str] = None
    image_url: Optional[str] = None
    character_positions: Optional[Dict[str, Any]] = None
    panel_layout: Optional[str] = Field(None, max_length=50)
    scene_order: Optional[int] = None

class EpisodeInDB(EpisodeBase):
    id: int
    webtoon_id: int
    image_url: Optional[str]
    character_positions: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EpisodeResponse(EpisodeInDB):
    pass

# Character schemas
class CharacterBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    role: Optional[str] = Field(None, max_length=50)

class CharacterCreate(CharacterBase):
    webtoon_id: int
    image_url: Optional[str] = None

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    role: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = None

class CharacterInDB(CharacterBase):
    id: int
    webtoon_id: int
    image_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CharacterResponse(CharacterInDB):
    pass

# Edit History schemas
class EditHistoryBase(BaseModel):
    edit_type: EditType
    original_content: Dict[str, Any]
    edited_content: Dict[str, Any]
    edit_command: Optional[str] = None

class EditHistoryCreate(EditHistoryBase):
    episode_id: int
    session_id: str

class EditHistoryInDB(EditHistoryBase):
    id: int
    episode_id: int
    session_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class EditHistoryResponse(EditHistoryInDB):
    pass

# Comment schemas
class CommentBase(BaseModel):
    content: str
    author_name: Optional[str] = "익명"

class CommentCreate(CommentBase):
    webtoon_id: int
    episode_id: Optional[int] = None
    parent_comment_id: Optional[int] = None
    session_id: Optional[str] = None

class CommentUpdate(BaseModel):
    content: str

class CommentInDB(CommentBase):
    id: int
    webtoon_id: int
    episode_id: Optional[int]
    parent_comment_id: Optional[int]
    session_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CommentResponse(CommentInDB):
    replies: List['CommentResponse'] = []
    is_owner: Optional[bool] = False

# Like schemas
class LikeCreate(BaseModel):
    webtoon_id: int
    session_id: str

class LikeResponse(BaseModel):
    id: int
    webtoon_id: int
    session_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat Message schemas
class ChatMessageBase(BaseModel):
    message: str
    sender_name: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    webtoon_id: int
    episode_id: Optional[int] = None
    sender_type: str = Field(..., pattern="^(user|character)$")
    character_id: Optional[int] = None
    parent_message_id: Optional[int] = None
    session_id: Optional[str] = None

class ChatMessageUpdate(BaseModel):
    is_read: Optional[bool] = None

class ChatMessageInDB(ChatMessageBase):
    id: int
    webtoon_id: int
    episode_id: Optional[int]
    sender_type: str
    session_id: Optional[str]
    is_read: bool
    character_id: Optional[int]
    parent_message_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessageResponse(ChatMessageInDB):
    character: Optional[CharacterResponse] = None
    replies: List['ChatMessageResponse'] = []
    is_owner: Optional[bool] = False

# Image Asset schemas
class ImageAssetBase(BaseModel):
    asset_type: str = Field(..., max_length=50)

class ImageAssetCreate(ImageAssetBase):
    file_path: str
    file_name: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = Field(None, max_length=50)
    width: Optional[int] = None
    height: Optional[int] = None
    webtoon_id: Optional[int] = None
    episode_id: Optional[int] = None
    session_id: Optional[str] = None

class ImageAssetInDB(ImageAssetBase):
    id: int
    file_path: str
    file_name: str
    file_size: Optional[int]
    mime_type: Optional[str]
    width: Optional[int]
    height: Optional[int]
    webtoon_id: Optional[int]
    episode_id: Optional[int]
    session_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImageAssetResponse(ImageAssetInDB):
    pass

# Generation Session schemas
class GenerationSessionCreate(BaseModel):
    input_text: str
    theme: Optional[str] = Field(None, max_length=200)
    story_style: Optional[str] = Field(None, max_length=100)
    original_language: Optional[str] = Field(None, max_length=10)
    llm_model: Optional[str] = Field(None, max_length=50)
    session_id: str

class GenerationSessionResponse(BaseModel):
    id: int
    session_id: str
    webtoon_id: Optional[int]
    input_text: str
    summary: Optional[str]
    theme: Optional[str]
    story_style: Optional[str]
    original_language: Optional[str]
    llm_model: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Pagination
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)