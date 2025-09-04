"""
Text2Cuts 웹툰 생성 데이터를 위한 MongoDB 모델
텍스트를 웹툰으로 변환하는 과정에서 생성되는 데이터 저장
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

# ==================== Enums ====================
class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CutType(str, Enum):
    ESTABLISHING = "establishing"  # 배경 설정 컷
    CHARACTER = "character"         # 캐릭터 중심 컷
    DIALOGUE = "dialogue"          # 대화 컷
    ACTION = "action"              # 액션 컷
    CLOSE_UP = "close_up"          # 클로즈업
    TRANSITION = "transition"      # 전환 컷

class AspectRatio(str, Enum):
    WEBTOON = "9:16"      # 세로형 웹툰
    SQUARE = "1:1"        # 정사각형
    LANDSCAPE = "16:9"    # 가로형
    PORTRAIT = "2:3"      # 세로형 표준

class StylePreset(str, Enum):
    MANHWA = "manhwa"              # 한국 웹툰 스타일
    MANGA = "manga"                # 일본 만화 스타일
    COMIC = "comic"                # 서양 코믹 스타일
    CARTOON = "cartoon"            # 카툰 스타일
    REALISTIC = "realistic"        # 사실적 스타일
    WATERCOLOR = "watercolor"      # 수채화 스타일
    DIGITAL_ART = "digital_art"    # 디지털 아트

# ==================== Sub Models ====================
class CharacterProfile(BaseModel):
    """캐릭터 프로필 정보"""
    name: str
    description: str
    visual_description: str  # 시각적 특징 설명
    personality: Optional[str] = None
    role: Optional[str] = None  # 주인공, 조연, 악역 등
    reference_prompt: Optional[str] = None  # 이미지 생성용 참조 프롬프트
    
class SceneBreakdown(BaseModel):
    """씬 분석 정보"""
    scene_number: int
    description: str
    location: Optional[str] = None
    time_of_day: Optional[str] = None
    mood: Optional[str] = None
    characters_present: List[str] = []

class CutData(BaseModel):
    """개별 컷(패널) 정보"""
    cut_number: int
    cut_type: CutType
    scene_number: int
    
    # 내용
    description: str
    dialogue: Optional[str] = None
    narration: Optional[str] = None
    sound_effects: List[str] = []
    
    # 시각적 정보
    camera_angle: Optional[str] = None  # 버드아이뷰, 클로즈업 등
    composition: Optional[str] = None   # 구도 설명
    
    # 이미지 생성 정보
    image_prompt: str
    negative_prompt: Optional[str] = None
    style_modifiers: List[str] = []
    
    # 생성된 이미지
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # 메타데이터
    generation_time: Optional[float] = None  # 생성 소요 시간(초)
    generation_model: Optional[str] = None
    generation_params: Dict[str, Any] = {}

class StoryboardData(BaseModel):
    """스토리보드 전체 정보"""
    total_scenes: int
    total_cuts: int
    scenes: List[SceneBreakdown]
    estimated_reading_time: Optional[int] = None  # 예상 읽기 시간(분)

class GenerationSettings(BaseModel):
    """이미지 생성 설정"""
    style_preset: StylePreset = StylePreset.MANHWA
    aspect_ratio: AspectRatio = AspectRatio.WEBTOON
    color_scheme: Optional[str] = None  # "vibrant", "pastel", "monochrome" 등
    art_style: Optional[str] = None
    
    # 이미지 생성 파라미터
    quality: str = "standard"  # "draft", "standard", "high"
    resolution: str = "1024x1536"
    model_name: Optional[str] = None
    seed: Optional[int] = None
    
    # 일관성 설정
    character_consistency: bool = True
    style_consistency: bool = True
    
class UserPreferences(BaseModel):
    """사용자 설정"""
    language: str = "ko"
    mature_content: bool = False
    violence_level: int = Field(0, ge=0, le=5)  # 0-5 폭력성 수준
    preferred_styles: List[StylePreset] = []
    
# ==================== Main Model ====================
class Text2CutsProject(BaseModel):
    """Text2Cuts 프로젝트 전체 데이터"""
    id: Optional[str] = Field(default=None, alias="_id", exclude=True)
    
    # 기본 정보
    project_id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: Optional[str] = None
    title: str
    original_text: str  # 원본 입력 텍스트
    
    # 분석 데이터
    characters: List[CharacterProfile] = []
    storyboard: Optional[StoryboardData] = None
    cuts: List[CutData] = []
    
    # 생성 설정
    settings: GenerationSettings
    user_preferences: Optional[UserPreferences] = None
    
    # 상태 관리
    status: GenerationStatus = GenerationStatus.PENDING
    progress: float = Field(0.0, ge=0.0, le=100.0)  # 진행률 (%)
    current_step: Optional[str] = None  # "analyzing", "generating", "post-processing"
    error_message: Optional[str] = None
    
    # 결과물
    final_webtoon_url: Optional[str] = None
    preview_images: List[str] = []
    download_formats: Dict[str, str] = {}  # {"pdf": "url", "zip": "url"}
    
    # 통계
    total_generation_time: Optional[float] = None  # 전체 소요 시간(초)
    tokens_used: Optional[int] = None
    credits_used: Optional[float] = None
    
    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # 버전 관리
    version: int = 1
    parent_project_id: Optional[str] = None  # 수정본인 경우 원본 ID
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }

# ==================== Analytics Models ====================
class GenerationAnalytics(BaseModel):
    """생성 통계 및 분석 데이터"""
    id: Optional[str] = Field(default=None, alias="_id", exclude=True)
    project_id: str
    
    # 텍스트 분석
    text_length: int
    word_count: int
    sentence_count: int
    detected_language: str
    
    # 생성 메트릭
    cuts_generated: int
    cuts_failed: int
    retry_count: int
    
    # 성능 메트릭
    text_analysis_time: float
    storyboard_generation_time: float
    image_generation_time: float
    total_time: float
    
    # 품질 메트릭
    consistency_score: Optional[float] = None  # 0-1
    style_adherence_score: Optional[float] = None  # 0-1
    
    # 사용자 피드백
    user_rating: Optional[int] = None  # 1-5
    user_feedback: Optional[str] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserHistory(BaseModel):
    """사용자 생성 히스토리"""
    id: Optional[str] = Field(default=None, alias="_id", exclude=True)
    user_id: str
    
    projects: List[Dict[str, Any]] = []  # 프로젝트 요약 정보
    total_projects: int = 0
    total_cuts_generated: int = 0
    total_credits_used: float = 0.0
    
    favorite_styles: List[StylePreset] = []
    average_project_length: float = 0.0
    
    last_active: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==================== Request/Response Models ====================
class Text2CutsRequest(BaseModel):
    """웹툰 생성 요청"""
    text: str
    title: Optional[str] = None
    settings: Optional[GenerationSettings] = None
    characters: Optional[List[Dict[str, str]]] = None  # 캐릭터 사전 정의
    
class Text2CutsResponse(BaseModel):
    """웹툰 생성 응답"""
    project_id: str
    status: GenerationStatus
    message: str
    preview_url: Optional[str] = None
    estimated_time: Optional[int] = None  # 예상 소요 시간(초)

class CutModifyRequest(BaseModel):
    """개별 컷 수정 요청"""
    project_id: str
    cut_number: int
    new_prompt: Optional[str] = None
    new_dialogue: Optional[str] = None
    regenerate_image: bool = False

class ProjectExportRequest(BaseModel):
    """프로젝트 내보내기 요청"""
    project_id: str
    format: str = "pdf"  # "pdf", "images", "json"
    quality: str = "high"
    include_metadata: bool = False