-- PostgreSQL Database Schema for GLTR Webtoon System
-- Version 1.0
-- Character Encoding: UTF-8

-- Drop existing tables if they exist
DROP TABLE IF EXISTS scene_characters CASCADE;
DROP TABLE IF EXISTS scenes CASCADE;
DROP TABLE IF EXISTS analyses CASCADE;
DROP TABLE IF EXISTS webtoons CASCADE;

-- =========================================
-- Table: webtoons (메인 웹툰 정보)
-- =========================================
CREATE TABLE webtoons (
    id SERIAL PRIMARY KEY,
    user_prompt TEXT NOT NULL,
    llm_prompt TEXT NOT NULL,
    prompt_summary TEXT,
    theme VARCHAR(255),
    style VARCHAR(100),
    output_language VARCHAR(50) NOT NULL DEFAULT 'korean',
    number_of_cuts SMALLINT NOT NULL DEFAULT 8 CHECK (number_of_cuts > 0 AND number_of_cuts <= 50),
    original_language VARCHAR(50) NOT NULL DEFAULT 'korean',
    story_guideline VARCHAR(255),
    first_audience_review BOOLEAN DEFAULT FALSE,
    fact_check BOOLEAN DEFAULT FALSE,
    scene_modification_request TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comments for webtoons table
COMMENT ON TABLE webtoons IS '웹툰 메인 정보 테이블';
COMMENT ON COLUMN webtoons.user_prompt IS '사용자가 입력한 프롬프트';
COMMENT ON COLUMN webtoons.llm_prompt IS 'LLM으로 전달된 프롬프트';
COMMENT ON COLUMN webtoons.prompt_summary IS '프롬프트 요약';
COMMENT ON COLUMN webtoons.theme IS '테마';
COMMENT ON COLUMN webtoons.style IS '스타일 (blog, fantasy, etc.)';
COMMENT ON COLUMN webtoons.output_language IS '출력 언어';
COMMENT ON COLUMN webtoons.number_of_cuts IS '만화 개수(컷 수)';
COMMENT ON COLUMN webtoons.original_language IS '원본 언어';
COMMENT ON COLUMN webtoons.story_guideline IS '스토리 가이드라인';
COMMENT ON COLUMN webtoons.first_audience_review IS '첫 번째 청중 검토 완료 여부';
COMMENT ON COLUMN webtoons.fact_check IS '팩트 체크 여부';
COMMENT ON COLUMN webtoons.scene_modification_request IS '장면 수정 요청';

-- =========================================
-- Table: scenes (씬 정보)
-- =========================================
CREATE TABLE scenes (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER NOT NULL,
    scene_number SMALLINT NOT NULL CHECK (scene_number > 0),
    summary TEXT,
    narrator TEXT,
    narrator_fact_check BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (webtoon_id, scene_number),
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Comments for scenes table
COMMENT ON TABLE scenes IS '웹툰 씬(장면) 정보 테이블';
COMMENT ON COLUMN scenes.scene_number IS '씬 번호';
COMMENT ON COLUMN scenes.summary IS '씬 요약';
COMMENT ON COLUMN scenes.narrator IS '내레이터 텍스트';
COMMENT ON COLUMN scenes.narrator_fact_check IS '내레이터 팩트 체크 여부';

-- =========================================
-- Table: scene_characters (씬별 캐릭터 대사)
-- =========================================
CREATE TABLE scene_characters (
    id SERIAL PRIMARY KEY,
    scene_id INTEGER NOT NULL,
    character_order SMALLINT NOT NULL CHECK (character_order > 0),
    character_name VARCHAR(100),
    dialogue TEXT,
    fact_check BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (scene_id, character_order),
    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Comments for scene_characters table
COMMENT ON TABLE scene_characters IS '씬별 캐릭터 정보 테이블';
COMMENT ON COLUMN scene_characters.character_order IS '캐릭터 순서 (1, 2, 3...)';
COMMENT ON COLUMN scene_characters.character_name IS '캐릭터 이름';
COMMENT ON COLUMN scene_characters.dialogue IS '캐릭터 대사';
COMMENT ON COLUMN scene_characters.fact_check IS '캐릭터 대사 팩트 체크 여부';

-- =========================================
-- Table: analyses (분석 내용)
-- =========================================
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    webtoon_id INTEGER NOT NULL,
    analysis_type VARCHAR(100),
    content TEXT NOT NULL,
    sequence_order SMALLINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Comments for analyses table
COMMENT ON TABLE analyses IS '웹툰 분석 내용 테이블';
COMMENT ON COLUMN analyses.analysis_type IS '분석 유형';
COMMENT ON COLUMN analyses.content IS '분석 내용';
COMMENT ON COLUMN analyses.sequence_order IS '분석 순서';

-- =========================================
-- Indexes for performance optimization
-- =========================================
CREATE INDEX idx_webtoons_created_at ON webtoons(created_at);
CREATE INDEX idx_webtoons_style_theme ON webtoons(style, theme);
CREATE INDEX idx_webtoons_fact_check ON webtoons(fact_check, first_audience_review);

CREATE INDEX idx_scenes_webtoon_id ON scenes(webtoon_id);
CREATE INDEX idx_scenes_fact_check ON scenes(narrator_fact_check);

CREATE INDEX idx_scene_characters_scene_id ON scene_characters(scene_id);
CREATE INDEX idx_scene_characters_fact_check ON scene_characters(fact_check);

CREATE INDEX idx_analyses_webtoon ON analyses(webtoon_id, sequence_order);

-- =========================================
-- Function: Update timestamp trigger
-- =========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
CREATE TRIGGER update_webtoons_updated_at BEFORE UPDATE ON webtoons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scenes_updated_at BEFORE UPDATE ON scenes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =========================================
-- Views for common queries (optional)
-- =========================================

-- View: Complete webtoon information with scene counts
CREATE VIEW v_webtoon_overview AS
SELECT 
    w.id,
    w.prompt_summary,
    w.theme,
    w.style,
    w.number_of_cuts,
    w.fact_check,
    w.first_audience_review,
    COUNT(DISTINCT s.id) as actual_scene_count,
    w.created_at
FROM webtoons w
LEFT JOIN scenes s ON w.id = s.webtoon_id
GROUP BY w.id, w.prompt_summary, w.theme, w.style, w.number_of_cuts, 
         w.fact_check, w.first_audience_review, w.created_at;

-- View: Scene details with character count
CREATE VIEW v_scene_details AS
SELECT 
    s.id as scene_id,
    s.webtoon_id,
    s.scene_number,
    s.summary,
    s.narrator,
    s.narrator_fact_check,
    COUNT(DISTINCT sc.id) as character_count
FROM scenes s
LEFT JOIN scene_characters sc ON s.id = sc.scene_id
GROUP BY s.id, s.webtoon_id, s.scene_number, s.summary, s.narrator, s.narrator_fact_check;

-- =========================================
-- Sample Data Insert (commented out)
-- =========================================
/*
-- 웹툰 삽입 예시
INSERT INTO webtoons (
    user_prompt, 
    llm_prompt, 
    prompt_summary, 
    theme, 
    style, 
    output_language, 
    number_of_cuts, 
    original_language, 
    story_guideline, 
    first_audience_review, 
    fact_check
) VALUES (
    '이재명 대통령은 4일 "지속 가능한 성장 토대 마련을 위해서는 경제의 핵심 근간인 제조업의 재도약이 필수"...',
    'Examples of commands you can add at the beginning...',
    '이재명 대통령은 제조업 재도약과 장바구니 물가 안정, 통신·금융사 해킹 대응을 강조했다...',
    '경제 활성화 및 민생 안정',
    'blog',
    'korean',
    8,
    'korean',
    'informational_blogtoon',
    TRUE,
    TRUE
) RETURNING id;

-- 씬 삽입 예시
INSERT INTO scenes (webtoon_id, scene_number, summary, narrator, narrator_fact_check)
VALUES (1, 1, '중소기업 대표의 고민', '김민수 대표는 15년째 정밀 부품을 만드는 중소기업을 운영하고 있습니다...', FALSE)
RETURNING id;

-- 캐릭터 삽입 예시
INSERT INTO scene_characters (scene_id, character_order, character_name, dialogue, fact_check)
VALUES (1, 1, '김민수', '하... 중국 업체들이 점점 따라잡고 있어. 우리 제품의 경쟁력이 예전 같지 않네.', TRUE);

-- 여러 캐릭터가 있는 경우
INSERT INTO scene_characters (scene_id, character_order, character_name, dialogue, fact_check)
VALUES 
    (2, 1, '박지영', '대표님, 새로운 정부 정책이 발표되었습니다!', FALSE),
    (2, 2, '김민수', '어떤 내용이지?', FALSE),
    (2, 3, '이철호', 'AI 전환 지원금이 대폭 늘어난다고 합니다.', TRUE);
*/

-- =========================================
-- Useful queries
-- =========================================
/*
-- 웹툰과 모든 씬, 캐릭터 정보 조회
SELECT 
    w.id as webtoon_id,
    w.prompt_summary,
    s.scene_number,
    s.narrator,
    sc.character_order,
    sc.character_name,
    sc.dialogue
FROM webtoons w
JOIN scenes s ON w.id = s.webtoon_id
LEFT JOIN scene_characters sc ON s.id = sc.scene_id
WHERE w.id = 1
ORDER BY s.scene_number, sc.character_order;

-- 팩트 체크가 완료된 웹툰 조회
SELECT * FROM webtoons 
WHERE fact_check = TRUE AND first_audience_review = TRUE;

-- 특정 웹툰의 분석 내용 조회
SELECT * FROM analyses 
WHERE webtoon_id = 1 
ORDER BY sequence_order;
*/
