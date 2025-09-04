-- MySQL Database Schema for GLTR Webtoon System
-- Version 1.0
-- Character Encoding: UTF-8

-- Drop existing tables if they exist
DROP TABLE IF EXISTS `scene_characters`;
DROP TABLE IF EXISTS `scenes`;
DROP TABLE IF EXISTS `analyses`;
DROP TABLE IF EXISTS `webtoons`;

-- =========================================
-- Table: webtoons (메인 웹툰 정보)
-- =========================================
CREATE TABLE `webtoons` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_prompt` TEXT NOT NULL COMMENT '사용자가 입력한 프롬프트',
    `llm_prompt` TEXT NOT NULL COMMENT 'LLM으로 전달된 프롬프트',
    `prompt_summary` TEXT COMMENT '프롬프트 요약',
    `theme` VARCHAR(255) COMMENT '테마',
    `style` VARCHAR(100) COMMENT '스타일 (blog, fantasy, etc.)',
    `output_language` VARCHAR(50) NOT NULL DEFAULT 'korean' COMMENT '출력 언어',
    `number_of_cuts` TINYINT UNSIGNED NOT NULL DEFAULT 8 COMMENT '만화 개수(컷 수)',
    `original_language` VARCHAR(50) NOT NULL DEFAULT 'korean' COMMENT '원본 언어',
    `story_guideline` VARCHAR(255) COMMENT '스토리 가이드라인',
    `first_audience_review` BOOLEAN DEFAULT FALSE COMMENT '첫 번째 청중 검토 완료 여부',
    `fact_check` BOOLEAN DEFAULT FALSE COMMENT '팩트 체크 여부',
    `scene_modification_request` TEXT COMMENT '장면 수정 요청',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_style_theme` (`style`, `theme`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='웹툰 메인 정보 테이블';

-- =========================================
-- Table: scenes (씬 정보)
-- =========================================
CREATE TABLE `scenes` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `webtoon_id` INT UNSIGNED NOT NULL,
    `scene_number` TINYINT UNSIGNED NOT NULL COMMENT '씬 번호',
    `summary` TEXT COMMENT '씬 요약',
    `narrator` TEXT COMMENT '내레이터 텍스트',
    `narrator_fact_check` BOOLEAN DEFAULT FALSE COMMENT '내레이터 팩트 체크 여부',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_webtoon_scene` (`webtoon_id`, `scene_number`),
    INDEX `idx_webtoon_id` (`webtoon_id`),
    CONSTRAINT `fk_scenes_webtoon` FOREIGN KEY (`webtoon_id`) 
        REFERENCES `webtoons` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='웹툰 씬(장면) 정보 테이블';

-- =========================================
-- Table: scene_characters (씬별 캐릭터 대사)
-- =========================================
CREATE TABLE `scene_characters` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `scene_id` INT UNSIGNED NOT NULL,
    `character_order` TINYINT UNSIGNED NOT NULL COMMENT '캐릭터 순서 (1, 2, 3...)',
    `character_name` VARCHAR(100) COMMENT '캐릭터 이름',
    `dialogue` TEXT COMMENT '캐릭터 대사',
    `fact_check` BOOLEAN DEFAULT FALSE COMMENT '캐릭터 대사 팩트 체크 여부',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_scene_character` (`scene_id`, `character_order`),
    INDEX `idx_scene_id` (`scene_id`),
    CONSTRAINT `fk_characters_scene` FOREIGN KEY (`scene_id`) 
        REFERENCES `scenes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='씬별 캐릭터 정보 테이블';

-- =========================================
-- Table: analyses (분석 내용)
-- =========================================
CREATE TABLE `analyses` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `webtoon_id` INT UNSIGNED NOT NULL,
    `analysis_type` VARCHAR(100) COMMENT '분석 유형',
    `content` TEXT NOT NULL COMMENT '분석 내용',
    `sequence_order` TINYINT UNSIGNED DEFAULT 0 COMMENT '분석 순서',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_webtoon_analysis` (`webtoon_id`, `sequence_order`),
    CONSTRAINT `fk_analyses_webtoon` FOREIGN KEY (`webtoon_id`) 
        REFERENCES `webtoons` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='웹툰 분석 내용 테이블';

-- =========================================
-- Indexes for performance optimization
-- =========================================
-- Additional composite indexes for common queries
CREATE INDEX `idx_webtoon_fact_check` ON `webtoons` (`fact_check`, `first_audience_review`);
CREATE INDEX `idx_scene_fact_check` ON `scenes` (`narrator_fact_check`);
CREATE INDEX `idx_character_fact_check` ON `scene_characters` (`fact_check`);

-- =========================================
-- Sample Data Insert (주석 처리됨)
-- =========================================
/*
-- 웹툰 삽입 예시
INSERT INTO `webtoons` (
    `user_prompt`, 
    `llm_prompt`, 
    `prompt_summary`, 
    `theme`, 
    `style`, 
    `output_language`, 
    `number_of_cuts`, 
    `original_language`, 
    `story_guideline`, 
    `first_audience_review`, 
    `fact_check`
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
);

-- 씬 삽입 예시
INSERT INTO `scenes` (`webtoon_id`, `scene_number`, `summary`, `narrator`, `narrator_fact_check`)
VALUES (1, 1, '중소기업 대표의 고민', '김민수 대표는 15년째 정밀 부품을 만드는 중소기업을 운영하고 있습니다...', FALSE);

-- 캐릭터 삽입 예시
INSERT INTO `scene_characters` (`scene_id`, `character_order`, `character_name`, `dialogue`, `fact_check`)
VALUES (1, 1, '김민수', '하... 중국 업체들이 점점 따라잡고 있어. 우리 제품의 경쟁력이 예전 같지 않네.', TRUE);
*/
