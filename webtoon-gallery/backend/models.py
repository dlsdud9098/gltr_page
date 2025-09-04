from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ImageType(str, Enum):
    THUMBNAIL = "thumbnail"
    EPISODE = "episode"
    CHARACTER_DESIGN = "character_design"
    STORYBOARD = "storyboard"

class Character(BaseModel):
    name: str
    description: str
    design_prompt: Optional[str] = None
    reference_images: List[str] = []

class StoryboardPanel(BaseModel):
    panel_number: int
    description: str
    dialogue: Optional[str] = None
    camera_angle: Optional[str] = None
    scene_prompt: Optional[str] = None

class WebtoonImage(BaseModel):
    url: str
    type: ImageType
    episode: Optional[int] = None
    panel_number: Optional[int] = None
    generation_prompt: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class Episode(BaseModel):
    episode_number: int
    title: str
    images: List[str]
    storyboard: List[StoryboardPanel] = []
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WebtoonEdit(BaseModel):
    drawing: Optional[str] = None
    llm_question: Optional[str] = None

class Webtoon(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id", exclude=True)
    title: str
    description: str
    genre: List[str] = []
    author: str
    thumbnail: str
    
    # 에피소드 관련
    episodes: List[Episode] = []
    total_episodes: int = 0
    
    # 제작 관련 데이터
    characters: List[Character] = []
    world_setting: Optional[str] = None
    main_prompt: Optional[str] = None
    style_prompt: Optional[str] = None
    
    # 이미지 데이터
    all_images: List[WebtoonImage] = []
    
    # 메타데이터
    tags: List[str] = []
    status: str = "ongoing"  # ongoing, completed, hiatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    view_count: int = 0
    like_count: int = 0
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WebtoonInDB(Webtoon):
    id: str = Field(alias="_id")

class WebtoonCreate(BaseModel):
    title: str
    description: str
    genre: List[str]
    author: str
    thumbnail: str
    world_setting: Optional[str] = None
    main_prompt: Optional[str] = None
    style_prompt: Optional[str] = None
    tags: List[str] = []

class WebtoonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    world_setting: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class PaginatedWebtoons(BaseModel):
    items: List[Webtoon]
    total: int
    page: int
    per_page: int
    has_more: bool