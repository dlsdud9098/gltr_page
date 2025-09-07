-- Migration script from old schema to new schema
-- Execute this script to update your existing database

-- 1. 백업 테이블 생성 (안전을 위해)
CREATE TABLE IF NOT EXISTS episodes_backup AS SELECT * FROM episodes;

-- 2. webtoons 테이블에 새 컬럼 추가
ALTER TABLE webtoons 
ADD COLUMN IF NOT EXISTS summary TEXT,
ADD COLUMN IF NOT EXISTS number_of_cuts INTEGER;

-- 3. scenes 테이블 생성 (episodes 데이터 마이그레이션)
CREATE TABLE IF NOT EXISTS scenes (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER REFERENCES webtoons(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL,
    scene_description TEXT,
    image_url VARCHAR(500),
    narration TEXT,
    character_positions JSONB,
    panel_layout VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(webtoon_id, scene_number)
);

-- 4. episodes 데이터를 scenes로 마이그레이션
INSERT INTO scenes (
    webtoon_id,
    scene_number,
    scene_description,
    image_url,
    narration,
    character_positions,
    panel_layout,
    created_at,
    updated_at
)
SELECT 
    webtoon_id,
    scene_order as scene_number,
    description as scene_description,
    image_url,
    narration,
    character_positions,
    panel_layout,
    created_at,
    updated_at
FROM episodes
ON CONFLICT (webtoon_id, scene_number) DO NOTHING;

-- 5. dialogues 테이블 생성
CREATE TABLE IF NOT EXISTS dialogues (
    id SERIAL PRIMARY KEY,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE,
    who_speaks VARCHAR(100) NOT NULL,
    dialogue TEXT NOT NULL,
    fact_or_fiction VARCHAR(20) DEFAULT 'fiction',
    dialogue_order INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(scene_id, dialogue_order)
);

-- 6. episodes의 dialogue 데이터를 dialogues 테이블로 마이그레이션
INSERT INTO dialogues (scene_id, who_speaks, dialogue, dialogue_order)
SELECT 
    s.id,
    'Unknown' as who_speaks,
    e.dialogue,
    1 as dialogue_order
FROM episodes e
JOIN scenes s ON e.webtoon_id = s.webtoon_id AND e.scene_order = s.scene_number
WHERE e.dialogue IS NOT NULL AND e.dialogue != ''
ON CONFLICT (scene_id, dialogue_order) DO NOTHING;

-- 7. generation_sessions 테이블에 새 컬럼 추가
ALTER TABLE generation_sessions
ADD COLUMN IF NOT EXISTS generation_result JSONB,
ADD COLUMN IF NOT EXISTS story_title VARCHAR(200),
ADD COLUMN IF NOT EXISTS number_of_cuts INTEGER;

-- 8. 외래키 참조 업데이트를 위한 임시 처리
-- edit_history 테이블 업데이트
ALTER TABLE edit_history ADD COLUMN IF NOT EXISTS scene_id INTEGER;
UPDATE edit_history eh
SET scene_id = s.id
FROM episodes e
JOIN scenes s ON e.webtoon_id = s.webtoon_id AND e.scene_order = s.scene_number
WHERE eh.episode_id = e.id;
ALTER TABLE edit_history ADD CONSTRAINT edit_history_scene_fk 
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE;

-- comments 테이블 업데이트
ALTER TABLE comments ADD COLUMN IF NOT EXISTS scene_id INTEGER;
UPDATE comments c
SET scene_id = s.id
FROM episodes e
JOIN scenes s ON e.webtoon_id = s.webtoon_id AND e.scene_order = s.scene_number
WHERE c.episode_id = e.id;
ALTER TABLE comments ADD CONSTRAINT comments_scene_fk 
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE;

-- image_assets 테이블 업데이트
ALTER TABLE image_assets ADD COLUMN IF NOT EXISTS scene_id INTEGER;
UPDATE image_assets ia
SET scene_id = s.id
FROM episodes e
JOIN scenes s ON e.webtoon_id = s.webtoon_id AND e.scene_order = s.scene_number
WHERE ia.episode_id = e.id;
ALTER TABLE image_assets ADD CONSTRAINT image_assets_scene_fk 
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE;

-- chat_messages 테이블 업데이트
ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS scene_id INTEGER;
UPDATE chat_messages cm
SET scene_id = s.id
FROM episodes e
JOIN scenes s ON e.webtoon_id = s.webtoon_id AND e.scene_order = s.scene_number
WHERE cm.episode_id = e.id;
ALTER TABLE chat_messages ADD CONSTRAINT chat_messages_scene_fk 
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE;

-- 9. 인덱스 재생성
DROP INDEX IF EXISTS idx_episodes_webtoon;
DROP INDEX IF EXISTS idx_episodes_order;
CREATE INDEX IF NOT EXISTS idx_scenes_webtoon ON scenes(webtoon_id);
CREATE INDEX IF NOT EXISTS idx_scenes_order ON scenes(webtoon_id, scene_number);
CREATE INDEX IF NOT EXISTS idx_dialogues_scene ON dialogues(scene_id);
CREATE INDEX IF NOT EXISTS idx_dialogues_order ON dialogues(scene_id, dialogue_order);
CREATE INDEX IF NOT EXISTS idx_edit_history_scene ON edit_history(scene_id);

-- 10. 트리거 업데이트
DROP TRIGGER IF EXISTS update_episodes_updated_at ON episodes;
CREATE TRIGGER update_scenes_updated_at BEFORE UPDATE ON scenes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 11. 이전 episode_id 컬럼 삭제 (선택사항 - 모든 것이 정상 작동하는지 확인 후 실행)
-- ALTER TABLE edit_history DROP COLUMN IF EXISTS episode_id;
-- ALTER TABLE comments DROP COLUMN IF EXISTS episode_id;
-- ALTER TABLE image_assets DROP COLUMN IF EXISTS episode_id;
-- ALTER TABLE chat_messages DROP COLUMN IF EXISTS episode_id;

-- 12. episodes 테이블 삭제 (선택사항 - 모든 것이 정상 작동하는지 확인 후 실행)
-- DROP TABLE IF EXISTS episodes;

-- 마이그레이션 완료 메시지
SELECT 'Migration completed successfully!' as message;