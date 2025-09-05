import asyncio
import os
from sqlalchemy import text
from database_postgresql import engine, init_db
from sqlalchemy.ext.asyncio import create_async_engine

async def create_database():
    # PostgreSQL 서버에 연결 (데이터베이스 없이)
    server_url = os.getenv(
        "POSTGRES_SERVER_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    )
    
    server_engine = create_async_engine(server_url, isolation_level="AUTOCOMMIT")
    
    async with server_engine.connect() as conn:
        # 데이터베이스 존재 여부 확인
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'webtoon_gallery'")
        )
        exists = result.scalar()
        
        if exists:
            print("Database 'webtoon_gallery' already exists. Dropping...")
            # 기존 연결 끊기
            await conn.execute(
                text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'webtoon_gallery'")
            )
            # 데이터베이스 삭제
            await conn.execute(text("DROP DATABASE webtoon_gallery"))
            print("Database dropped.")
        
        # 데이터베이스 생성
        print("Creating database 'webtoon_gallery'...")
        await conn.execute(text("CREATE DATABASE webtoon_gallery"))
        print("Database created successfully!")
    
    await server_engine.dispose()
    
    # 테이블 생성
    print("Creating tables...")
    await init_db()
    print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_database())