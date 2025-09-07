-- GLTR Webtoon Platform Database Schema (Updated for Text2Cuts)
-- PostgreSQL Database Schema

-- 웹툰/작품 테이블 (수정됨)
CREATE TABLE IF NOT EXISTS webtoons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    summary TEXT, -- 추가: 스토리 요약
    description TEXT,
    thumbnail_url VARCHAR(500),
    author_name VARCHAR(100) DEFAULT 'Anonymous',
    genre VARCHAR(50),
    theme VARCHAR(100), -- 기존 필드 유지
    story_style VARCHAR(100), -- 기존 필드 유지 (fantasy, romance, action 등)
    number_of_cuts INTEGER, -- 추가: 컷 수
    status VARCHAR(20) DEFAULT 'published', -- draft, published, completed
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    session_id VARCHAR(100), -- 브라우저 세션으로 소유권 확인
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 장면 테이블 (episodes 테이블을 scenes로 변경)
CREATE TABLE IF NOT EXISTS scenes (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER REFERENCES webtoons(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL, -- scene_order를 scene_number로 변경
    scene_description TEXT, -- description을 scene_description으로 명확히 변경
    image_url VARCHAR(500),
    narration TEXT,
    character_positions JSONB, -- 캐릭터 위치 정보
    panel_layout VARCHAR(50), -- 패널 레이아웃 타입
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(webtoon_id, scene_number)
);

-- 대화 테이블 (신규 추가)
CREATE TABLE IF NOT EXISTS dialogues (
    id SERIAL PRIMARY KEY,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE,
    who_speaks VARCHAR(100) NOT NULL, -- 화자
    dialogue TEXT NOT NULL, -- 대사
    fact_or_fiction VARCHAR(20) DEFAULT 'fiction', -- fact or fiction
    dialogue_order INTEGER DEFAULT 1, -- 같은 장면 내 대화 순서
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(scene_id, dialogue_order)
);

-- 캐릭터 테이블
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER REFERENCES webtoons(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    appearance TEXT,
    personality TEXT,
    role VARCHAR(50), -- main, supporting, minor
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 편집 이력 테이블
CREATE TABLE IF NOT EXISTS edit_history (
    id SERIAL PRIMARY KEY,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE, -- episode_id를 scene_id로 변경
    session_id VARCHAR(100), -- 브라우저 세션 ID
    edit_type VARCHAR(50), -- text, image, layout, dialogue
    original_content JSONB,
    edited_content JSONB,
    edit_command TEXT, -- AI 수정 명령어 (있는 경우)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 댓글 테이블
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER REFERENCES webtoons(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE, -- episode_id를 scene_id로 변경
    author_name VARCHAR(100) DEFAULT '익명',
    content TEXT NOT NULL,
    parent_comment_id INTEGER REFERENCES comments(id),
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI 생성 세션 테이블 (text2cuts 기능용 - 수정됨)
CREATE TABLE IF NOT EXISTS generation_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    webtoon_id INTEGER REFERENCES webtoons(id),
    input_text TEXT,
    generation_result JSONB, -- 추가: 생성된 전체 JSON 결과 저장
    summary TEXT,
    theme VARCHAR(200),
    story_style VARCHAR(100),
    story_title VARCHAR(200), -- 추가: 생성된 스토리 제목
    number_of_cuts INTEGER, -- 추가: 생성된 컷 수
    original_language VARCHAR(10),
    llm_model VARCHAR(50), -- gpt-4, claude, etc.
    status VARCHAR(20), -- processing, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 이미지 자산 테이블
CREATE TABLE IF NOT EXISTS image_assets (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(50),
    width INTEGER,
    height INTEGER,
    webtoon_id INTEGER REFERENCES webtoons(id),
    scene_id INTEGER REFERENCES scenes(id), -- episode_id를 scene_id로 변경
    asset_type VARCHAR(50), -- thumbnail, panel, character, background
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 좋아요 테이블 (세션 기반)
CREATE TABLE IF NOT EXISTS likes (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER REFERENCES webtoons(id) ON DELETE CASCADE,
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(webtoon_id, session_id)
);

-- 채팅 메시지 테이블 (캐릭터와의 대화)
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER REFERENCES webtoons(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenes(id), -- episode_id를 scene_id로 변경
    sender_type VARCHAR(20) NOT NULL, -- 'user' or 'character'
    sender_name VARCHAR(100),
    message TEXT NOT NULL,
    session_id VARCHAR(100),
    is_read BOOLEAN DEFAULT FALSE,
    character_id INTEGER REFERENCES characters(id),
    parent_message_id INTEGER REFERENCES chat_messages(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_webtoons_status ON webtoons(status);
CREATE INDEX idx_webtoons_session ON webtoons(session_id);
CREATE INDEX idx_scenes_webtoon ON scenes(webtoon_id);
CREATE INDEX idx_scenes_order ON scenes(webtoon_id, scene_number);
CREATE INDEX idx_dialogues_scene ON dialogues(scene_id);
CREATE INDEX idx_dialogues_order ON dialogues(scene_id, dialogue_order);
CREATE INDEX idx_characters_webtoon ON characters(webtoon_id);
CREATE INDEX idx_edit_history_scene ON edit_history(scene_id);
CREATE INDEX idx_comments_webtoon ON comments(webtoon_id);
CREATE INDEX idx_generation_sessions_session ON generation_sessions(session_id);
CREATE INDEX idx_likes_webtoon ON likes(webtoon_id);
CREATE INDEX idx_likes_session ON likes(session_id);
CREATE INDEX idx_chat_messages_webtoon ON chat_messages(webtoon_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_character ON chat_messages(character_id);
CREATE INDEX idx_chat_messages_parent ON chat_messages(parent_message_id);

-- Trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_webtoons_updated_at BEFORE UPDATE ON webtoons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scenes_updated_at BEFORE UPDATE ON scenes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();