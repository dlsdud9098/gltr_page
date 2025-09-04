"""
Database utilities for GLTR Webtoon System
Helper functions for common database operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.models import Webtoon, Scene, SceneCharacter, Analysis, DatabaseConnection
import json


class WebtoonDBManager:
    """Manager class for webtoon database operations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_webtoon_with_scenes(self, webtoon_data: Dict[str, Any]) -> int:
        """
        Create a complete webtoon with all scenes and characters
        
        Args:
            webtoon_data: Dictionary containing webtoon information and scenes
        
        Returns:
            Created webtoon ID
        """
        session = self.db.get_session()
        
        try:
            # Create webtoon
            webtoon = Webtoon(
                user_prompt=webtoon_data['user_prompt'],
                llm_prompt=webtoon_data['llm_prompt'],
                prompt_summary=webtoon_data.get('prompt_summary'),
                theme=webtoon_data.get('theme'),
                style=webtoon_data.get('style'),
                output_language=webtoon_data.get('output_language', 'korean'),
                number_of_cuts=webtoon_data.get('number_of_cuts', 8),
                original_language=webtoon_data.get('original_language', 'korean'),
                story_guideline=webtoon_data.get('story_guideline'),
                first_audience_review=webtoon_data.get('first_audience_review', False),
                fact_check=webtoon_data.get('fact_check', False),
                scene_modification_request=webtoon_data.get('scene_modification_request')
            )
            session.add(webtoon)
            session.flush()
            
            # Add scenes
            for scene_data in webtoon_data.get('scenes', []):
                scene = Scene(
                    webtoon_id=webtoon.id,
                    scene_number=scene_data['scene_number'],
                    summary=scene_data.get('summary'),
                    narrator=scene_data.get('narrator'),
                    narrator_fact_check=scene_data.get('narrator_fact_check', False)
                )
                session.add(scene)
                session.flush()
                
                # Add characters for this scene
                for char_data in scene_data.get('characters', []):
                    character = SceneCharacter(
                        scene_id=scene.id,
                        character_order=char_data['character_order'],
                        character_name=char_data.get('character_name'),
                        dialogue=char_data.get('dialogue'),
                        fact_check=char_data.get('fact_check', False)
                    )
                    session.add(character)
            
            # Add analyses
            for idx, analysis_data in enumerate(webtoon_data.get('analyses', [])):
                analysis = Analysis(
                    webtoon_id=webtoon.id,
                    analysis_type=analysis_data.get('type'),
                    content=analysis_data['content'],
                    sequence_order=analysis_data.get('sequence_order', idx)
                )
                session.add(analysis)
            
            session.commit()
            return webtoon.id
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_webtoon_complete(self, webtoon_id: int) -> Optional[Dict[str, Any]]:
        """
        Get complete webtoon information including all scenes and characters
        
        Args:
            webtoon_id: Webtoon ID
        
        Returns:
            Complete webtoon data as dictionary
        """
        session = self.db.get_session()
        
        try:
            webtoon = session.query(Webtoon).filter_by(id=webtoon_id).first()
            if not webtoon:
                return None
            
            result = {
                'id': webtoon.id,
                'user_prompt': webtoon.user_prompt,
                'llm_prompt': webtoon.llm_prompt,
                'prompt_summary': webtoon.prompt_summary,
                'theme': webtoon.theme,
                'style': webtoon.style,
                'output_language': webtoon.output_language,
                'number_of_cuts': webtoon.number_of_cuts,
                'original_language': webtoon.original_language,
                'story_guideline': webtoon.story_guideline,
                'first_audience_review': webtoon.first_audience_review,
                'fact_check': webtoon.fact_check,
                'scene_modification_request': webtoon.scene_modification_request,
                'created_at': webtoon.created_at.isoformat() if webtoon.created_at else None,
                'scenes': [],
                'analyses': []
            }
            
            # Get scenes with characters
            for scene in webtoon.scenes:
                scene_data = {
                    'scene_number': scene.scene_number,
                    'summary': scene.summary,
                    'narrator': scene.narrator,
                    'narrator_fact_check': scene.narrator_fact_check,
                    'characters': []
                }
                
                for character in scene.characters:
                    scene_data['characters'].append({
                        'character_order': character.character_order,
                        'character_name': character.character_name,
                        'dialogue': character.dialogue,
                        'fact_check': character.fact_check
                    })
                
                result['scenes'].append(scene_data)
            
            # Get analyses
            for analysis in webtoon.analyses:
                result['analyses'].append({
                    'type': analysis.analysis_type,
                    'content': analysis.content,
                    'sequence_order': analysis.sequence_order
                })
            
            return result
            
        finally:
            session.close()
    
    def update_scene_dialogue(self, scene_id: int, character_order: int, 
                            new_dialogue: str, fact_check: bool = False) -> bool:
        """
        Update character dialogue in a scene
        
        Args:
            scene_id: Scene ID
            character_order: Character order in the scene
            new_dialogue: New dialogue text
            fact_check: Whether fact check has been done
        
        Returns:
            Success status
        """
        session = self.db.get_session()
        
        try:
            character = session.query(SceneCharacter).filter_by(
                scene_id=scene_id,
                character_order=character_order
            ).first()
            
            if character:
                character.dialogue = new_dialogue
                character.fact_check = fact_check
                session.commit()
                return True
            return False
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def search_webtoons(self, **filters) -> List[Dict[str, Any]]:
        """
        Search webtoons with various filters
        
        Args:
            **filters: Keyword arguments for filtering (theme, style, fact_check, etc.)
        
        Returns:
            List of matching webtoons
        """
        session = self.db.get_session()
        
        try:
            query = session.query(Webtoon)
            
            # Apply filters
            if 'theme' in filters:
                query = query.filter(Webtoon.theme.contains(filters['theme']))
            if 'style' in filters:
                query = query.filter_by(style=filters['style'])
            if 'fact_check' in filters:
                query = query.filter_by(fact_check=filters['fact_check'])
            if 'first_audience_review' in filters:
                query = query.filter_by(first_audience_review=filters['first_audience_review'])
            
            results = []
            for webtoon in query.all():
                results.append({
                    'id': webtoon.id,
                    'prompt_summary': webtoon.prompt_summary,
                    'theme': webtoon.theme,
                    'style': webtoon.style,
                    'number_of_cuts': webtoon.number_of_cuts,
                    'created_at': webtoon.created_at.isoformat() if webtoon.created_at else None
                })
            
            return results
            
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Statistics dictionary
        """
        session = self.db.get_session()
        
        try:
            stats = {
                'total_webtoons': session.query(Webtoon).count(),
                'total_scenes': session.query(Scene).count(),
                'total_characters': session.query(SceneCharacter).count(),
                'total_analyses': session.query(Analysis).count(),
                'fact_checked_webtoons': session.query(Webtoon).filter_by(fact_check=True).count(),
                'reviewed_webtoons': session.query(Webtoon).filter_by(first_audience_review=True).count(),
                'styles': {}
            }
            
            # Count by style
            styles = session.query(Webtoon.style).distinct().all()
            for (style,) in styles:
                if style:
                    stats['styles'][style] = session.query(Webtoon).filter_by(style=style).count()
            
            return stats
            
        finally:
            session.close()


# Example data structure for testing
def get_sample_webtoon_data() -> Dict[str, Any]:
    """Get sample webtoon data for testing"""
    return {
        'user_prompt': '이재명 대통령은 4일 "지속 가능한 성장 토대 마련을 위해서는...',
        'llm_prompt': 'Examples of commands you can add at the beginning...',
        'prompt_summary': '이재명 대통령은 제조업 재도약과 장바구니 물가 안정...',
        'theme': '경제 활성화 및 민생 안정',
        'style': 'blog',
        'output_language': 'korean',
        'number_of_cuts': 8,
        'original_language': 'korean',
        'story_guideline': 'informational_blogtoon',
        'first_audience_review': True,
        'fact_check': True,
        'scenes': [
            {
                'scene_number': 1,
                'summary': '중소기업 대표의 고민',
                'narrator': '김민수 대표는 15년째 정밀 부품을 만드는 중소기업을 운영하고 있습니다...',
                'narrator_fact_check': False,
                'characters': [
                    {
                        'character_order': 1,
                        'character_name': '김민수',
                        'dialogue': '하... 중국 업체들이 점점 따라잡고 있어...',
                        'fact_check': True
                    }
                ]
            },
            {
                'scene_number': 2,
                'summary': '정부 정책 발표',
                'narrator': '정부에서 제조업 지원 정책을 발표했습니다.',
                'narrator_fact_check': True,
                'characters': [
                    {
                        'character_order': 1,
                        'character_name': '박지영',
                        'dialogue': '대표님, 새로운 정부 정책이 발표되었습니다!',
                        'fact_check': False
                    },
                    {
                        'character_order': 2,
                        'character_name': '김민수',
                        'dialogue': '어떤 내용이지?',
                        'fact_check': False
                    },
                    {
                        'character_order': 3,
                        'character_name': '이철호',
                        'dialogue': 'AI 전환 지원금이 대폭 늘어난다고 합니다.',
                        'fact_check': True
                    }
                ]
            }
        ],
        'analyses': [
            {
                'type': 'economic_impact',
                'content': '제조업 재도약 정책이 중소기업에 미치는 영향 분석',
                'sequence_order': 1
            },
            {
                'type': 'security_concerns',
                'content': '금융사 보안 사고 증가에 따른 대응 방안',
                'sequence_order': 2
            }
        ]
    }


if __name__ == "__main__":
    # Example usage
    # db_url = "sqlite:///test_gltr_webtoon.db"
    db_url = "postgresql://username:password@localhost/gltr_webtoon"
    
    # Initialize database
    db_conn = DatabaseConnection(db_url)
    db_conn.create_tables()
    
    # Initialize manager
    manager = WebtoonDBManager(db_conn)
    
    # Create a webtoon
    sample_data = get_sample_webtoon_data()
    webtoon_id = manager.create_webtoon_with_scenes(sample_data)
    print(f"Created webtoon with ID: {webtoon_id}")
    
    # Get complete webtoon data
    webtoon_data = manager.get_webtoon_complete(webtoon_id)
    print(f"Retrieved webtoon: {json.dumps(webtoon_data, indent=2, ensure_ascii=False)}")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"Database statistics: {json.dumps(stats, indent=2)}")
