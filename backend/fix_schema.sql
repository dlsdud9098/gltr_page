-- Fix foreign key type mismatches
-- Update likes table
ALTER TABLE likes DROP CONSTRAINT IF EXISTS likes_webtoon_id_fkey;
ALTER TABLE likes ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- Update scenes table  
ALTER TABLE scenes DROP CONSTRAINT IF EXISTS scenes_webtoon_id_fkey;
ALTER TABLE scenes ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- Update comments table
ALTER TABLE comments DROP CONSTRAINT IF EXISTS comments_webtoon_id_fkey;
ALTER TABLE comments ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- Update chat_messages table
ALTER TABLE chat_messages DROP CONSTRAINT IF EXISTS chat_messages_webtoon_id_fkey;
ALTER TABLE chat_messages ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- Update characters table
ALTER TABLE characters DROP CONSTRAINT IF EXISTS characters_webtoon_id_fkey;
ALTER TABLE characters ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- Update generation_sessions table
ALTER TABLE generation_sessions DROP CONSTRAINT IF EXISTS generation_sessions_webtoon_id_fkey;
ALTER TABLE generation_sessions ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- Update image_assets table
ALTER TABLE image_assets DROP CONSTRAINT IF EXISTS image_assets_webtoon_id_fkey;
ALTER TABLE image_assets ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- Re-add foreign key constraints
ALTER TABLE likes ADD CONSTRAINT likes_webtoon_id_fkey 
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE;

ALTER TABLE scenes ADD CONSTRAINT scenes_webtoon_id_fkey 
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE;

ALTER TABLE comments ADD CONSTRAINT comments_webtoon_id_fkey 
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE;

ALTER TABLE chat_messages ADD CONSTRAINT chat_messages_webtoon_id_fkey 
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE;

ALTER TABLE characters ADD CONSTRAINT characters_webtoon_id_fkey 
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE;

ALTER TABLE generation_sessions ADD CONSTRAINT generation_sessions_webtoon_id_fkey 
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE;

ALTER TABLE image_assets ADD CONSTRAINT image_assets_webtoon_id_fkey 
    FOREIGN KEY (webtoon_id) REFERENCES webtoons(id) ON DELETE CASCADE;