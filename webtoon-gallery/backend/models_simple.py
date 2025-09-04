from pydantic import BaseModel
from typing import List, Optional, Any

class WebtoonSimple(BaseModel):
    id: str
    title: str
    description: str
    author: str
    thumbnail: str
    total_episodes: int
    images: List[str] = []

class PaginatedWebtoonsSimple(BaseModel):
    items: List[WebtoonSimple]
    total: int
    page: int
    per_page: int
    has_more: bool

class WebtoonEdit(BaseModel):
    drawing: Optional[str] = None
    llm_question: Optional[str] = None