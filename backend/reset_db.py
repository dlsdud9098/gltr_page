"""
Initialize or reset the database (No Auth Version)
Run this script to create all tables fresh
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'gltr_webtoon')
}

def reset_database():
    """Drop and recreate all tables"""
    conn = None
    cur = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Connected to database")
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Drop all tables first (in reverse order of dependencies)
        drop_tables = """
        DROP TABLE IF EXISTS chat_messages CASCADE;
        DROP TABLE IF EXISTS likes CASCADE;
        DROP TABLE IF EXISTS image_assets CASCADE;
        DROP TABLE IF EXISTS generation_sessions CASCADE;
        DROP TABLE IF EXISTS comments CASCADE;
        DROP TABLE IF EXISTS edit_history CASCADE;
        DROP TABLE IF EXISTS characters CASCADE;
        DROP TABLE IF EXISTS episodes CASCADE;
        DROP TABLE IF EXISTS webtoons CASCADE;
        """
        
        print("Dropping existing tables...")
        cur.execute(drop_tables)
        conn.commit()
        
        print("Creating new tables...")
        cur.execute(schema_sql)
        conn.commit()
        
        print("Database initialized successfully!")
        
        # Add sample data
        print("Adding sample data...")
        
        # Sample webtoon
        cur.execute("""
            INSERT INTO webtoons (title, description, author_name, genre, theme, story_style)
            VALUES 
            ('모험의 시작', '평범한 소년이 마법 세계로 떨어지며 시작되는 대모험', 'GLTR', '판타지', '모험', 'adventure'),
            ('학교 일상', '고등학생들의 재미있는 일상 이야기', 'GLTR', '일상', '학교', 'slice-of-life')
            RETURNING id
        """)
        webtoon_ids = [row[0] for row in cur.fetchall()]
        
        # Sample episodes
        for webtoon_id in webtoon_ids:
            cur.execute("""
                INSERT INTO episodes (webtoon_id, episode_number, scene_order, title, dialogue, description)
                VALUES 
                (%s, 1, 1, '첫 만남', '안녕하세요!', '주인공이 처음 등장하는 장면'),
                (%s, 1, 2, '모험 시작', '이제 시작이야!', '모험이 시작되는 장면')
            """, (webtoon_id, webtoon_id))
        
        # Sample characters
        for webtoon_id in webtoon_ids:
            cur.execute("""
                INSERT INTO characters (webtoon_id, name, description, role)
                VALUES 
                (%s, '주인공', '용감하고 정의로운 성격', '주인공')
            """, (webtoon_id,))
        
        conn.commit()
        print("Sample data added successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    response = input("This will drop all existing tables and data. Continue? (yes/no): ")
    if response.lower() == 'yes':
        reset_database()
    else:
        print("Cancelled.")