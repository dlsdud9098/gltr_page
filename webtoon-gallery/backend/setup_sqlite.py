#!/usr/bin/env python3
"""
SQLite Database Setup Script (Alternative to PostgreSQL)
Creates tables and inserts test data for the GLTR Webtoon System
"""

import sqlite3
import random
from datetime import datetime, timedelta
import json
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent / 'webtoon.db'

# Test data templates
THEMES = ['로맨스', '액션', '판타지', '일상', '스릴러', '코미디', '드라마', 'SF', '미스터리', '역사']
STYLES = ['blog', 'fantasy', 'realistic', 'cartoon', 'webtoon', 'manga', 'comic']
LANGUAGES = ['korean', 'english', 'japanese', 'chinese']
CHARACTER_NAMES = ['김민수', '이서연', '박지훈', '최유진', '정하늘', '강태양', '윤소라', '임도현', '한지우', '조예린']

def create_schema():
    """Create SQLite schema (simplified version of PostgreSQL schema)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS scene_characters")
    cursor.execute("DROP TABLE IF EXISTS scenes")
    cursor.execute("DROP TABLE IF EXISTS analyses")
    cursor.execute("DROP TABLE IF EXISTS webtoons")
    
    # Create webtoons table
    cursor.execute("""
        CREATE TABLE webtoons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_prompt TEXT NOT NULL,
            llm_prompt TEXT NOT NULL,
            prompt_summary TEXT,
            theme VARCHAR(255),
            style VARCHAR(100),
            output_language VARCHAR(50) NOT NULL DEFAULT 'korean',
            number_of_cuts INTEGER NOT NULL DEFAULT 8,
            original_language VARCHAR(50) NOT NULL DEFAULT 'korean',
            story_guideline VARCHAR(255),
            first_audience_review BOOLEAN DEFAULT 0,
            fact_check BOOLEAN DEFAULT 0,
            scene_modification_request TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create scenes table
    cursor.execute("""
        CREATE TABLE scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            webtoon_id INTEGER NOT NULL,
            scene_number INTEGER NOT NULL,
            summary TEXT,
            narrator TEXT,
            narrator_fact_check BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (webtoon_id, scene_number),
            FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE
        )
    """)
    
    # Create scene_characters table
    cursor.execute("""
        CREATE TABLE scene_characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scene_id INTEGER NOT NULL,
            character_order INTEGER NOT NULL,
            character_name VARCHAR(100),
            dialogue TEXT,
            fact_check BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (scene_id, character_order),
            FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE
        )
    """)
    
    # Create analyses table
    cursor.execute("""
        CREATE TABLE analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            webtoon_id INTEGER NOT NULL,
            analysis_type VARCHAR(100),
            content TEXT NOT NULL,
            sequence_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_webtoons_created_at ON webtoons(created_at)")
    cursor.execute("CREATE INDEX idx_webtoons_style_theme ON webtoons(style, theme)")
    cursor.execute("CREATE INDEX idx_scenes_webtoon_id ON scenes(webtoon_id)")
    cursor.execute("CREATE INDEX idx_scene_characters_scene_id ON scene_characters(scene_id)")
    cursor.execute("CREATE INDEX idx_analyses_webtoon ON analyses(webtoon_id, sequence_order)")
    
    conn.commit()
    print("SQLite schema created successfully")
    
    cursor.close()
    conn.close()

def generate_test_data():
    """Generate 10 test webtoon records with scenes and characters"""
    test_webtoons = []
    
    for i in range(10):
        theme = random.choice(THEMES)
        style = random.choice(STYLES)
        num_cuts = random.randint(4, 12)
        
        webtoon = {
            'user_prompt': f'{theme} 장르의 웹툰을 만들어주세요. 주인공이 {random.choice(["모험", "성장", "사랑", "복수", "우정"])}을 통해 성장하는 이야기입니다.',
            'llm_prompt': f'Create a {style} style webtoon with {theme} theme. The story should have {num_cuts} scenes.',
            'prompt_summary': f'{theme} 장르 웹툰 - {num_cuts}개 장면',
            'theme': theme,
            'style': style,
            'output_language': random.choice(LANGUAGES),
            'number_of_cuts': num_cuts,
            'original_language': 'korean',
            'story_guideline': f'{style}_guideline',
            'first_audience_review': random.choice([1, 0]),
            'fact_check': random.choice([1, 0]),
            'scene_modification_request': random.choice([None, '캐릭터 표정 수정 필요', '배경 디테일 추가', None]),
            'scenes': []
        }
        
        # Generate scenes for each webtoon
        for scene_num in range(1, min(num_cuts + 1, 6)):  # Limit to 5 scenes for test data
            scene = {
                'scene_number': scene_num,
                'summary': f'장면 {scene_num}: {random.choice(["갈등", "전개", "절정", "해결", "시작"])} 부분',
                'narrator': f'이곳은 {random.choice(["평화로운", "위험한", "신비한", "활기찬", "조용한"])} {random.choice(["마을", "도시", "숲", "학교", "회사"])}입니다...',
                'narrator_fact_check': random.choice([1, 0]),
                'characters': []
            }
            
            # Add 1-3 characters per scene
            num_characters = random.randint(1, 3)
            for char_order in range(1, num_characters + 1):
                character = {
                    'character_order': char_order,
                    'character_name': random.choice(CHARACTER_NAMES),
                    'dialogue': random.choice([
                        "이게 정말 맞는 길일까요?",
                        "우리가 해낼 수 있을 거예요!",
                        "잠깐, 뭔가 이상한데...",
                        "드디어 찾았다!",
                        "이제 시작이야.",
                        "포기하지 마세요.",
                        "믿을 수 없어...",
                        "함께라면 가능해요!"
                    ]),
                    'fact_check': random.choice([1, 0])
                }
                scene['characters'].append(character)
            
            webtoon['scenes'].append(scene)
        
        # Add analyses
        webtoon['analyses'] = [
            {
                'analysis_type': 'story_structure',
                'content': f'{theme} 장르의 전형적인 구조를 따르며, {num_cuts}개의 장면으로 구성됨',
                'sequence_order': 1
            },
            {
                'analysis_type': 'character_development',
                'content': '주인공의 성장이 명확하게 드러나는 스토리라인',
                'sequence_order': 2
            }
        ]
        
        test_webtoons.append(webtoon)
    
    return test_webtoons

def insert_test_data(test_webtoons):
    """Insert test data into SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        for idx, webtoon_data in enumerate(test_webtoons, 1):
            # Insert webtoon
            cursor.execute("""
                INSERT INTO webtoons (
                    user_prompt, llm_prompt, prompt_summary, theme, style,
                    output_language, number_of_cuts, original_language,
                    story_guideline, first_audience_review, fact_check,
                    scene_modification_request
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                webtoon_data['user_prompt'],
                webtoon_data['llm_prompt'],
                webtoon_data['prompt_summary'],
                webtoon_data['theme'],
                webtoon_data['style'],
                webtoon_data['output_language'],
                webtoon_data['number_of_cuts'],
                webtoon_data['original_language'],
                webtoon_data['story_guideline'],
                webtoon_data['first_audience_review'],
                webtoon_data['fact_check'],
                webtoon_data['scene_modification_request']
            ))
            
            webtoon_id = cursor.lastrowid
            
            # Insert scenes
            for scene in webtoon_data['scenes']:
                cursor.execute("""
                    INSERT INTO scenes (
                        webtoon_id, scene_number, summary, narrator, narrator_fact_check
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    webtoon_id,
                    scene['scene_number'],
                    scene['summary'],
                    scene['narrator'],
                    scene['narrator_fact_check']
                ))
                
                scene_id = cursor.lastrowid
                
                # Insert characters
                for character in scene['characters']:
                    cursor.execute("""
                        INSERT INTO scene_characters (
                            scene_id, character_order, character_name, dialogue, fact_check
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        scene_id,
                        character['character_order'],
                        character['character_name'],
                        character['dialogue'],
                        character['fact_check']
                    ))
            
            # Insert analyses
            for analysis in webtoon_data['analyses']:
                cursor.execute("""
                    INSERT INTO analyses (
                        webtoon_id, analysis_type, content, sequence_order
                    ) VALUES (?, ?, ?, ?)
                """, (
                    webtoon_id,
                    analysis['analysis_type'],
                    analysis['content'],
                    analysis['sequence_order']
                ))
            
            print(f"Inserted webtoon {idx}: {webtoon_data['prompt_summary']}")
        
        conn.commit()
        print("\nAll test data inserted successfully!")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM webtoons")
        webtoon_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM scenes")
        scene_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM scene_characters")
        character_count = cursor.fetchone()[0]
        
        print(f"\nDatabase statistics:")
        print(f"- Webtoons: {webtoon_count}")
        print(f"- Scenes: {scene_count}")
        print(f"- Characters: {character_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Main execution function"""
    print("Starting SQLite setup...")
    
    # Step 1: Create schema
    create_schema()
    
    # Step 2: Generate test data
    print("\nGenerating test data...")
    test_webtoons = generate_test_data()
    
    # Step 3: Insert test data
    print("\nInserting test data...")
    insert_test_data(test_webtoons)
    
    print(f"\nSQLite database created at: {DB_PATH}")
    print("Setup complete!")

if __name__ == "__main__":
    main()