"""
Schema migration script to update database structure
"""
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="gltr_webtoon",
    user="postgres",
    password="1234"
)

cursor = conn.cursor()

# Add missing columns to webtoons table
alter_queries = [
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500)",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS author_name VARCHAR(100) DEFAULT 'Anonymous'",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS genre VARCHAR(50)",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS theme VARCHAR(100)",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS story_style VARCHAR(100)",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS number_of_cuts INTEGER",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'published'",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS like_count INTEGER DEFAULT 0",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS session_id VARCHAR(100)",
    "ALTER TABLE webtoons ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
]

print("Updating webtoons table...")
for query in alter_queries:
    try:
        cursor.execute(query)
        print(f"  ✓ Executed: {query[:50]}...")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Add missing columns to scenes table
scene_queries = [
    "ALTER TABLE scenes ADD COLUMN IF NOT EXISTS scene_description TEXT",
    "ALTER TABLE scenes ADD COLUMN IF NOT EXISTS image_url VARCHAR(500)",
    "ALTER TABLE scenes ADD COLUMN IF NOT EXISTS narration TEXT",
    "ALTER TABLE scenes ADD COLUMN IF NOT EXISTS character_positions JSON",
    "ALTER TABLE scenes ADD COLUMN IF NOT EXISTS panel_layout VARCHAR(50)",
    "ALTER TABLE scenes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
]

print("\nUpdating scenes table...")
for query in scene_queries:
    try:
        cursor.execute(query)
        print(f"  ✓ Executed: {query[:50]}...")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Add missing columns to dialogues table
dialogue_queries = [
    "ALTER TABLE dialogues ADD COLUMN IF NOT EXISTS fact_or_fiction VARCHAR(20) DEFAULT 'fiction'",
    "ALTER TABLE dialogues ADD COLUMN IF NOT EXISTS dialogue_order INTEGER DEFAULT 1"
]

print("\nUpdating dialogues table...")
for query in dialogue_queries:
    try:
        cursor.execute(query)
        print(f"  ✓ Executed: {query[:50]}...")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Commit changes
conn.commit()
print("\n✅ Schema migration completed successfully!")

# Check current data
cursor.execute("SELECT COUNT(*) FROM webtoons")
webtoon_count = cursor.fetchone()[0]
print(f"\nCurrent webtoons count: {webtoon_count}")

cursor.execute("SELECT COUNT(*) FROM scenes")
scene_count = cursor.fetchone()[0]
print(f"Current scenes count: {scene_count}")

cursor.execute("SELECT COUNT(*) FROM dialogues")
dialogue_count = cursor.fetchone()[0]
print(f"Current dialogues count: {dialogue_count}")

cursor.close()
conn.close()