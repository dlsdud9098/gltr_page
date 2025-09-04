"""
Database connection and helper functions for SQLite
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Any, Optional

# Database file path
DB_PATH = Path(__file__).parent / 'webtoon.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()

def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a sqlite3.Row to a dictionary"""
    return dict(zip(row.keys(), row))

class WebtoonDB:
    """Database operations for webtoons"""
    
    @staticmethod
    def get_all_webtoons(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get paginated webtoons"""
        offset = (page - 1) * per_page
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM webtoons")
            total = cursor.fetchone()['total']
            
            # Get paginated webtoons
            cursor.execute("""
                SELECT 
                    w.id,
                    w.prompt_summary as title,
                    w.theme as description,
                    w.style as author,
                    w.number_of_cuts as total_episodes,
                    w.created_at
                FROM webtoons w
                ORDER BY w.created_at DESC
                LIMIT ? OFFSET ?
            """, (per_page, offset))
            
            webtoons = []
            for row in cursor.fetchall():
                webtoon = dict_from_row(row)
                # Convert ID to string for compatibility
                webtoon_id = str(webtoon['id'])
                
                # Format webtoon data to match the model
                formatted_webtoon = {
                    'id': webtoon_id,
                    'title': webtoon['title'] or f"웹툰 #{webtoon_id}",
                    'description': webtoon['description'] or '설명 없음',
                    'author': webtoon['author'] or 'Unknown',
                    'thumbnail': f"/api/images/thumbnail_{webtoon_id}.jpg",
                    'total_episodes': webtoon.get('total_episodes', 0),
                    'images': []
                }
                
                # Get scenes for images
                cursor.execute("""
                    SELECT scene_number, summary 
                    FROM scenes 
                    WHERE webtoon_id = ? 
                    ORDER BY scene_number 
                    LIMIT 3
                """, (webtoon['id'],))
                
                scenes = cursor.fetchall()
                formatted_webtoon['images'] = [f"/api/images/webtoon_{webtoon_id}_scene_{s['scene_number']}.jpg" 
                                              for s in scenes]
                
                webtoons.append(formatted_webtoon)
            
            has_more = (page * per_page) < total
            
            return {
                'items': webtoons,
                'total': total,
                'page': page,
                'per_page': per_page,
                'has_more': has_more
            }
    
    @staticmethod
    def get_webtoon_by_id(webtoon_id: int) -> Optional[Dict[str, Any]]:
        """Get a single webtoon with full details"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get webtoon details
            cursor.execute("""
                SELECT 
                    w.id,
                    w.prompt_summary as title,
                    w.theme as description,
                    w.style as author,
                    w.number_of_cuts as total_episodes,
                    w.user_prompt,
                    w.llm_prompt,
                    w.output_language,
                    w.fact_check,
                    w.created_at
                FROM webtoons w
                WHERE w.id = ?
            """, (webtoon_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            webtoon = dict_from_row(row)
            
            # Convert ID to string for compatibility
            webtoon['id'] = str(webtoon['id'])
            
            # Add thumbnail
            webtoon['thumbnail'] = f"/api/images/thumbnail_{webtoon['id']}.jpg"
            
            # Get all scenes
            cursor.execute("""
                SELECT 
                    s.id,
                    s.scene_number,
                    s.summary,
                    s.narrator,
                    s.narrator_fact_check
                FROM scenes s
                WHERE s.webtoon_id = ?
                ORDER BY s.scene_number
            """, (webtoon_id,))
            
            scenes = []
            for scene_row in cursor.fetchall():
                scene = dict_from_row(scene_row)
                
                # Get characters for each scene
                cursor.execute("""
                    SELECT 
                        character_order,
                        character_name,
                        dialogue,
                        fact_check
                    FROM scene_characters
                    WHERE scene_id = ?
                    ORDER BY character_order
                """, (scene['id'],))
                
                scene['characters'] = [dict_from_row(char) for char in cursor.fetchall()]
                scenes.append(scene)
            
            webtoon['scenes'] = scenes
            
            # Generate image URLs for each scene
            webtoon['images'] = [f"/api/images/webtoon_{webtoon_id}_scene_{s['scene_number']}.jpg" 
                                for s in scenes]
            
            # Get analyses
            cursor.execute("""
                SELECT 
                    analysis_type,
                    content,
                    sequence_order
                FROM analyses
                WHERE webtoon_id = ?
                ORDER BY sequence_order
            """, (webtoon_id,))
            
            webtoon['analyses'] = [dict_from_row(row) for row in cursor.fetchall()]
            
            return webtoon
    
    @staticmethod
    def search_webtoons(query: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search webtoons by theme or summary"""
        offset = (page - 1) * per_page
        search_pattern = f'%{query}%'
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM webtoons 
                WHERE prompt_summary LIKE ? OR theme LIKE ?
            """, (search_pattern, search_pattern))
            total = cursor.fetchone()['total']
            
            # Get paginated search results
            cursor.execute("""
                SELECT 
                    w.id,
                    w.prompt_summary as title,
                    w.theme as description,
                    w.style as author,
                    w.number_of_cuts as total_episodes,
                    w.created_at
                FROM webtoons w
                WHERE w.prompt_summary LIKE ? OR w.theme LIKE ?
                ORDER BY w.created_at DESC
                LIMIT ? OFFSET ?
            """, (search_pattern, search_pattern, per_page, offset))
            
            webtoons = [dict_from_row(row) for row in cursor.fetchall()]
            
            # Add thumbnail for each webtoon
            for webtoon in webtoons:
                # Convert ID to string for compatibility
                webtoon['id'] = str(webtoon['id'])
                webtoon['thumbnail'] = f"/api/images/thumbnail_{webtoon['id']}.jpg"
            
            has_more = (page * per_page) < total
            
            return {
                'items': webtoons,
                'total': total,
                'page': page,
                'per_page': per_page,
                'has_more': has_more
            }