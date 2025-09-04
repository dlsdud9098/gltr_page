"""
SQLAlchemy ORM Models for GLTR Webtoon Database
Compatible with both MySQL and PostgreSQL
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean, 
    DateTime, ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Webtoon(Base):
    """웹툰 메인 정보 테이블"""
    __tablename__ = 'webtoons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_prompt = Column(Text, nullable=False, comment='사용자가 입력한 프롬프트')
    llm_prompt = Column(Text, nullable=False, comment='LLM으로 전달된 프롬프트')
    prompt_summary = Column(Text, comment='프롬프트 요약')
    theme = Column(String(255), comment='테마')
    style = Column(String(100), comment='스타일 (blog, fantasy, etc.)')
    output_language = Column(String(50), nullable=False, default='korean', comment='출력 언어')
    number_of_cuts = Column(Integer, nullable=False, default=8, comment='만화 개수(컷 수)')
    original_language = Column(String(50), nullable=False, default='korean', comment='원본 언어')
    story_guideline = Column(String(255), comment='스토리 가이드라인')
    first_audience_review = Column(Boolean, default=False, comment='첫 번째 청중 검토 완료 여부')
    fact_check = Column(Boolean, default=False, comment='팩트 체크 여부')
    scene_modification_request = Column(Text, comment='장면 수정 요청')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scenes = relationship('Scene', back_populates='webtoon', cascade='all, delete-orphan')
    analyses = relationship('Analysis', back_populates='webtoon', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        Index('idx_created_at', 'created_at'),
        Index('idx_style_theme', 'style', 'theme'),
        Index('idx_webtoon_fact_check', 'fact_check', 'first_audience_review'),
    )
    
    def __repr__(self):
        return f"<Webtoon(id={self.id}, theme={self.theme}, style={self.style})>"


class Scene(Base):
    """웹툰 씬(장면) 정보 테이블"""
    __tablename__ = 'scenes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id', ondelete='CASCADE'), nullable=False)
    scene_number = Column(Integer, nullable=False, comment='씬 번호')
    summary = Column(Text, comment='씬 요약')
    narrator = Column(Text, comment='내레이터 텍스트')
    narrator_fact_check = Column(Boolean, default=False, comment='내레이터 팩트 체크 여부')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    webtoon = relationship('Webtoon', back_populates='scenes')
    characters = relationship('SceneCharacter', back_populates='scene', cascade='all, delete-orphan')
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('webtoon_id', 'scene_number', name='uk_webtoon_scene'),
        Index('idx_webtoon_id', 'webtoon_id'),
        Index('idx_scene_fact_check', 'narrator_fact_check'),
        CheckConstraint('scene_number > 0', name='check_scene_number_positive'),
    )
    
    def __repr__(self):
        return f"<Scene(id={self.id}, webtoon_id={self.webtoon_id}, scene_number={self.scene_number})>"


class SceneCharacter(Base):
    """씬별 캐릭터 정보 테이블"""
    __tablename__ = 'scene_characters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scene_id = Column(Integer, ForeignKey('scenes.id', ondelete='CASCADE'), nullable=False)
    character_order = Column(Integer, nullable=False, comment='캐릭터 순서 (1, 2, 3...)')
    character_name = Column(String(100), comment='캐릭터 이름')
    dialogue = Column(Text, comment='캐릭터 대사')
    fact_check = Column(Boolean, default=False, comment='캐릭터 대사 팩트 체크 여부')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scene = relationship('Scene', back_populates='characters')
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('scene_id', 'character_order', name='uk_scene_character'),
        Index('idx_scene_id', 'scene_id'),
        Index('idx_character_fact_check', 'fact_check'),
        CheckConstraint('character_order > 0', name='check_character_order_positive'),
    )
    
    def __repr__(self):
        return f"<SceneCharacter(id={self.id}, scene_id={self.scene_id}, character_name={self.character_name})>"


class Analysis(Base):
    """웹툰 분석 내용 테이블"""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    webtoon_id = Column(Integer, ForeignKey('webtoons.id', ondelete='CASCADE'), nullable=False)
    analysis_type = Column(String(100), comment='분석 유형')
    content = Column(Text, nullable=False, comment='분석 내용')
    sequence_order = Column(Integer, default=0, comment='분석 순서')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webtoon = relationship('Webtoon', back_populates='analyses')
    
    # Indexes
    __table_args__ = (
        Index('idx_webtoon_analysis', 'webtoon_id', 'sequence_order'),
    )
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, webtoon_id={self.webtoon_id}, type={self.analysis_type})>"


# Database connection helper
class DatabaseConnection:
    """Database connection and session management"""
    
    def __init__(self, database_url: str):
        """
        Initialize database connection
        
        Args:
            database_url: Database URL string
                MySQL: 'mysql+pymysql://user:password@localhost/dbname'
                PostgreSQL: 'postgresql://user:password@localhost/dbname'
        """
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all tables from the database"""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()


# Example usage
if __name__ == "__main__":
    # MySQL connection example
    # db_url = "mysql+pymysql://username:password@localhost/gltr_webtoon"
    
    # PostgreSQL connection example
    # db_url = "postgresql://username:password@localhost/gltr_webtoon"
    
    # SQLite for testing
    db_url = "sqlite:///gltr_webtoon.db"
    
    # Initialize connection
    db = DatabaseConnection(db_url)
    
    # Create tables
    db.create_tables()
    
    # Example: Insert data
    session = db.get_session()
    
    try:
        # Create a new webtoon
        webtoon = Webtoon(
            user_prompt="이재명 대통령은 4일...",
            llm_prompt="Examples of commands...",
            prompt_summary="이재명 대통령은 제조업 재도약과...",
            theme="경제 활성화 및 민생 안정",
            style="blog",
            number_of_cuts=8,
            story_guideline="informational_blogtoon",
            first_audience_review=True,
            fact_check=True
        )
        session.add(webtoon)
        session.flush()  # Get the ID
        
        # Create a scene
        scene = Scene(
            webtoon_id=webtoon.id,
            scene_number=1,
            summary="중소기업 대표의 고민",
            narrator="김민수 대표는 15년째 정밀 부품을 만드는 중소기업을 운영하고 있습니다...",
            narrator_fact_check=False
        )
        session.add(scene)
        session.flush()
        
        # Add character to scene
        character = SceneCharacter(
            scene_id=scene.id,
            character_order=1,
            character_name="김민수",
            dialogue="하... 중국 업체들이 점점 따라잡고 있어. 우리 제품의 경쟁력이 예전 같지 않네.",
            fact_check=True
        )
        session.add(character)
        
        # Add analysis
        analysis = Analysis(
            webtoon_id=webtoon.id,
            analysis_type="economic_impact",
            content="제조업 재도약 정책이 중소기업에 미치는 영향 분석",
            sequence_order=1
        )
        session.add(analysis)
        
        # Commit all changes
        session.commit()
        print("Data inserted successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()
