-- Fix all remaining foreign key type mismatches

-- chat_messages table
ALTER TABLE chat_messages ALTER COLUMN webtoon_id TYPE UUID USING NULL;
ALTER TABLE chat_messages ALTER COLUMN scene_id TYPE UUID USING NULL;
ALTER TABLE chat_messages ALTER COLUMN character_id TYPE UUID USING NULL;
ALTER TABLE chat_messages ALTER COLUMN parent_message_id TYPE UUID USING NULL;

-- comments table
ALTER TABLE comments ALTER COLUMN webtoon_id TYPE UUID USING NULL;
ALTER TABLE comments ALTER COLUMN scene_id TYPE UUID USING NULL;
ALTER TABLE comments ALTER COLUMN parent_comment_id TYPE UUID USING NULL;

-- dialogues table
ALTER TABLE dialogues ALTER COLUMN scene_id TYPE UUID USING NULL;

-- edit_history table
ALTER TABLE edit_history ALTER COLUMN scene_id TYPE UUID USING NULL;

-- generation_sessions table
ALTER TABLE generation_sessions ALTER COLUMN webtoon_id TYPE UUID USING NULL;

-- image_assets table
ALTER TABLE image_assets ALTER COLUMN webtoon_id TYPE UUID USING NULL;
ALTER TABLE image_assets ALTER COLUMN scene_id TYPE UUID USING NULL;