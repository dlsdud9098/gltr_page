from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import os
import random
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from database_postgresql import get_session, init_db, close_db
from models_postgresql import (
    Webtoon, Episode, Character, WebtoonImage, StoryboardPanel,
    Genre, Tag, StatusEnum, ImageTypeEnum,
    WebtoonCreate, WebtoonUpdate, WebtoonEdit,
    WebtoonResponse, PaginatedWebtoons
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await initialize_sample_data()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://publisher.gltr-ous.us",
        "http://publisher.gltr-ous.us"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
IMAGES_DIR = STATIC_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

async def get_or_create_genre(session: AsyncSession, genre_name: str) -> Genre:
    result = await session.execute(
        select(Genre).where(Genre.name == genre_name)
    )
    genre = result.scalar_one_or_none()
    if not genre:
        genre = Genre(name=genre_name)
        session.add(genre)
        await session.flush()
    return genre

async def get_or_create_tag(session: AsyncSession, tag_name: str) -> Tag:
    result = await session.execute(
        select(Tag).where(Tag.name == tag_name)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=tag_name)
        session.add(tag)
        await session.flush()
    return tag

async def initialize_sample_data():
    from database_postgresql import async_session_maker
    
    async with async_session_maker() as session:
        result = await session.execute(select(func.count()).select_from(Webtoon))
        count = result.scalar()
        
        if count == 0:
            print("Initializing sample data...")
            await create_sample_webtoons(session)
            await session.commit()
            print("Sample data created successfully")

async def create_sample_webtoons(session: AsyncSession):
    genres = ["로맨스", "액션", "판타지", "일상", "개그", "스릴러", "드라마", "미스터리", "스포츠", "SF"]
    titles_prefix = ["신비한", "전설의", "최강의", "마법", "비밀", "특별한", "숨겨진", "놀라운", "위대한", "진짜"]
    titles_suffix = ["이야기", "모험", "세계", "전설", "영웅", "일기", "여정", "대결", "도전", "생활"]
    
    character_names = ["주인공", "라이벌", "조력자", "악역", "히로인"]
    style_prompts = [
        "웹툰 스타일, 밝고 화려한 색상",
        "만화 스타일, 부드러운 라인",
        "애니메이션 스타일, 디테일한 표현",
        "미니멀리즘 스타일, 깔끔한 구성"
    ]
    
    for i in range(1, 101):
        thumbnail_index = ((i - 1) % 3) + 1
        num_episodes = random.randint(1, 5)
        
        # Create webtoon
        webtoon = Webtoon(
            title=f"{random.choice(titles_prefix)} {random.choice(titles_suffix)} {i}",
            description=f"웹툰 {i}번의 흥미진진한 이야기. 독자들에게 사랑받는 작품입니다.",
            author=f"작가{chr(65 + (i % 26))}",
            thumbnail=f"/static/images/webtoon{thumbnail_index}/ep1_1.jpg",
            total_episodes=num_episodes,
            world_setting=f"웹툰 {i}의 세계관: {random.choice(['현대', '판타지', '미래', '과거', '이세계'])} 배경",
            main_prompt=f"웹툰 {i}: {random.choice(titles_prefix)} {random.choice(titles_suffix)}의 메인 스토리",
            style_prompt=random.choice(style_prompts),
            status=random.choice(list(StatusEnum)),
            view_count=random.randint(100, 10000),
            like_count=random.randint(10, 1000)
        )
        
        # Add genres
        selected_genres = random.sample(genres, random.randint(1, 3))
        for genre_name in selected_genres:
            genre = await get_or_create_genre(session, genre_name)
            webtoon.genres.append(genre)
        
        # Add tags
        for j in range(1, random.randint(3, 6)):
            tag = await get_or_create_tag(session, f"태그{j}")
            webtoon.tags.append(tag)
        
        session.add(webtoon)
        await session.flush()
        
        # Add episodes
        for ep_num in range(1, num_episodes + 1):
            num_images = random.randint(4, 5)
            episode_images = []
            
            for img_num in range(1, num_images + 1):
                image_url = f"/static/images/webtoon{thumbnail_index}/ep1_{img_num}.jpg"
                episode_images.append(image_url)
            
            episode = Episode(
                webtoon_id=webtoon.id,
                episode_number=ep_num,
                title=f"에피소드 {ep_num}: {random.choice(titles_prefix)} {random.choice(titles_suffix)}",
                images=episode_images
            )
            session.add(episode)
            await session.flush()
            
            # Add storyboard panels
            for img_num in range(1, num_images + 1):
                panel = StoryboardPanel(
                    episode_id=episode.id,
                    panel_number=img_num,
                    description=f"장면 {img_num}: 캐릭터가 등장하여 이야기를 전개",
                    dialogue=f"대사 {img_num}" if random.choice([True, False]) else None,
                    camera_angle=random.choice(["클로즈업", "미디엄샷", "롱샷", "버드아이뷰"]),
                    scene_prompt=f"웹툰 스타일, 에피소드 {ep_num} 장면 {img_num}"
                )
                session.add(panel)
        
        # Add characters
        for char_idx, char_name in enumerate(random.sample(character_names, min(3, len(character_names)))):
            character = Character(
                webtoon_id=webtoon.id,
                name=f"{char_name} {i}-{char_idx}",
                description=f"웹툰 {i}의 {char_name} 캐릭터",
                design_prompt=f"{char_name} 캐릭터, {random.choice(style_prompts)}",
                reference_images=[f"/static/images/webtoon{thumbnail_index}/ep1_1.jpg"]
            )
            session.add(character)
        
        # Add images
        # Thumbnail
        thumbnail_image = WebtoonImage(
            webtoon_id=webtoon.id,
            url=f"/static/images/webtoon{thumbnail_index}/ep1_1.jpg",
            type=ImageTypeEnum.THUMBNAIL,
            generation_prompt=f"썸네일 이미지, {random.choice(style_prompts)}"
        )
        session.add(thumbnail_image)
        
        # Episode images
        for ep_num in range(1, num_episodes + 1):
            for img_num in range(1, random.randint(4, 6)):
                image = WebtoonImage(
                    webtoon_id=webtoon.id,
                    url=f"/static/images/webtoon{thumbnail_index}/ep1_{img_num}.jpg",
                    type=ImageTypeEnum.EPISODE,
                    episode=ep_num,
                    panel_number=img_num,
                    generation_prompt=f"{random.choice(style_prompts)}, 에피소드 {ep_num} 컷 {img_num}"
                )
                session.add(image)

@app.get("/")
def read_root():
    return {"message": "Webtoon Gallery API with PostgreSQL"}

@app.get("/api/webtoons", response_model=PaginatedWebtoons)
async def get_webtoons(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    genre: Optional[str] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    # Build query
    query = select(Webtoon).options(
        selectinload(Webtoon.genres),
        selectinload(Webtoon.tags),
        selectinload(Webtoon.episodes),
        selectinload(Webtoon.characters),
        selectinload(Webtoon.images)
    )
    
    # Apply filters
    filters = []
    if genre:
        query = query.join(Webtoon.genres).where(Genre.name == genre)
    if status:
        filters.append(Webtoon.status == status)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Count total
    count_query = select(func.count()).select_from(Webtoon)
    if genre:
        count_query = count_query.join(Webtoon.genres).where(Genre.name == genre)
    if status:
        count_query = count_query.where(Webtoon.status == status)
    
    result = await session.execute(count_query)
    total = result.scalar()
    
    # Pagination
    skip = (page - 1) * per_page
    query = query.offset(skip).limit(per_page)
    
    result = await session.execute(query)
    webtoons = result.scalars().all()
    
    # Convert to response models
    items = []
    for webtoon in webtoons:
        item_dict = {
            "id": webtoon.id,
            "title": webtoon.title,
            "description": webtoon.description,
            "author": webtoon.author,
            "thumbnail": webtoon.thumbnail,
            "genre": [g.name for g in webtoon.genres],
            "total_episodes": webtoon.total_episodes,
            "episodes": [
                {
                    "episode_number": e.episode_number,
                    "title": e.title,
                    "images": e.images,
                    "created_at": e.created_at
                } for e in webtoon.episodes
            ],
            "characters": [
                {
                    "name": c.name,
                    "description": c.description,
                    "design_prompt": c.design_prompt,
                    "reference_images": c.reference_images
                } for c in webtoon.characters
            ],
            "all_images": [
                {
                    "url": img.url,
                    "type": img.type.value,
                    "episode": img.episode,
                    "panel_number": img.panel_number,
                    "generation_prompt": img.generation_prompt,
                    "generated_at": img.generated_at
                } for img in webtoon.images
            ],
            "tags": [t.name for t in webtoon.tags],
            "status": webtoon.status.value,
            "created_at": webtoon.created_at,
            "updated_at": webtoon.updated_at,
            "view_count": webtoon.view_count,
            "like_count": webtoon.like_count
        }
        items.append(WebtoonResponse(**item_dict))
    
    has_more = skip + per_page < total
    
    return PaginatedWebtoons(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        has_more=has_more
    )

@app.get("/api/webtoons/{webtoon_id}", response_model=WebtoonResponse)
async def get_webtoon(
    webtoon_id: int,
    session: AsyncSession = Depends(get_session)
):
    query = select(Webtoon).options(
        selectinload(Webtoon.genres),
        selectinload(Webtoon.tags),
        selectinload(Webtoon.episodes),
        selectinload(Webtoon.characters),
        selectinload(Webtoon.images)
    ).where(Webtoon.id == webtoon_id)
    
    result = await session.execute(query)
    webtoon = result.scalar_one_or_none()
    
    if not webtoon:
        raise HTTPException(status_code=404, detail="Webtoon not found")
    
    return WebtoonResponse(
        id=webtoon.id,
        title=webtoon.title,
        description=webtoon.description,
        author=webtoon.author,
        thumbnail=webtoon.thumbnail,
        genre=[g.name for g in webtoon.genres],
        total_episodes=webtoon.total_episodes,
        episodes=[
            {
                "episode_number": e.episode_number,
                "title": e.title,
                "images": e.images,
                "created_at": e.created_at
            } for e in webtoon.episodes
        ],
        characters=[
            {
                "name": c.name,
                "description": c.description,
                "design_prompt": c.design_prompt,
                "reference_images": c.reference_images
            } for c in webtoon.characters
        ],
        all_images=[
            {
                "url": img.url,
                "type": img.type.value,
                "episode": img.episode,
                "panel_number": img.panel_number,
                "generation_prompt": img.generation_prompt,
                "generated_at": img.generated_at
            } for img in webtoon.images
        ],
        tags=[t.name for t in webtoon.tags],
        status=webtoon.status.value,
        created_at=webtoon.created_at,
        updated_at=webtoon.updated_at,
        view_count=webtoon.view_count,
        like_count=webtoon.like_count
    )

@app.post("/api/webtoons", response_model=WebtoonResponse)
async def create_webtoon(
    webtoon_data: WebtoonCreate,
    session: AsyncSession = Depends(get_session)
):
    webtoon = Webtoon(
        title=webtoon_data.title,
        description=webtoon_data.description,
        author=webtoon_data.author,
        thumbnail=webtoon_data.thumbnail,
        world_setting=webtoon_data.world_setting,
        main_prompt=webtoon_data.main_prompt,
        style_prompt=webtoon_data.style_prompt,
        status=StatusEnum(webtoon_data.status),
        total_episodes=0,
        view_count=0,
        like_count=0
    )
    
    # Add genres
    for genre_name in webtoon_data.genre:
        genre = await get_or_create_genre(session, genre_name)
        webtoon.genres.append(genre)
    
    # Add tags
    for tag_name in webtoon_data.tags:
        tag = await get_or_create_tag(session, tag_name)
        webtoon.tags.append(tag)
    
    session.add(webtoon)
    await session.commit()
    await session.refresh(webtoon)
    
    return WebtoonResponse(
        id=webtoon.id,
        title=webtoon.title,
        description=webtoon.description,
        author=webtoon.author,
        thumbnail=webtoon.thumbnail,
        genre=[g.name for g in webtoon.genres],
        total_episodes=0,
        episodes=[],
        characters=[],
        all_images=[],
        tags=[t.name for t in webtoon.tags],
        status=webtoon.status.value,
        created_at=webtoon.created_at,
        updated_at=webtoon.updated_at,
        view_count=webtoon.view_count,
        like_count=webtoon.like_count
    )

@app.put("/api/webtoons/{webtoon_id}", response_model=WebtoonResponse)
async def update_webtoon(
    webtoon_id: int,
    update_data: WebtoonUpdate,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Webtoon).options(
            selectinload(Webtoon.genres),
            selectinload(Webtoon.tags)
        ).where(Webtoon.id == webtoon_id)
    )
    webtoon = result.scalar_one_or_none()
    
    if not webtoon:
        raise HTTPException(status_code=404, detail="Webtoon not found")
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        if field not in ['genre', 'tags'] and value is not None:
            setattr(webtoon, field, value)
    
    # Update genres if provided
    if update_data.genre is not None:
        webtoon.genres.clear()
        for genre_name in update_data.genre:
            genre = await get_or_create_genre(session, genre_name)
            webtoon.genres.append(genre)
    
    # Update tags if provided
    if update_data.tags is not None:
        webtoon.tags.clear()
        for tag_name in update_data.tags:
            tag = await get_or_create_tag(session, tag_name)
            webtoon.tags.append(tag)
    
    webtoon.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(webtoon)
    
    # Load related data
    await session.execute(
        select(Webtoon).options(
            selectinload(Webtoon.episodes),
            selectinload(Webtoon.characters),
            selectinload(Webtoon.images)
        ).where(Webtoon.id == webtoon_id)
    )
    
    return WebtoonResponse(
        id=webtoon.id,
        title=webtoon.title,
        description=webtoon.description,
        author=webtoon.author,
        thumbnail=webtoon.thumbnail,
        genre=[g.name for g in webtoon.genres],
        total_episodes=webtoon.total_episodes,
        episodes=[
            {
                "episode_number": e.episode_number,
                "title": e.title,
                "images": e.images,
                "created_at": e.created_at
            } for e in webtoon.episodes
        ],
        characters=[
            {
                "name": c.name,
                "description": c.description,
                "design_prompt": c.design_prompt,
                "reference_images": c.reference_images
            } for c in webtoon.characters
        ],
        all_images=[
            {
                "url": img.url,
                "type": img.type.value,
                "episode": img.episode,
                "panel_number": img.panel_number,
                "generation_prompt": img.generation_prompt,
                "generated_at": img.generated_at
            } for img in webtoon.images
        ],
        tags=[t.name for t in webtoon.tags],
        status=webtoon.status.value,
        created_at=webtoon.created_at,
        updated_at=webtoon.updated_at,
        view_count=webtoon.view_count,
        like_count=webtoon.like_count
    )

@app.delete("/api/webtoons/{webtoon_id}")
async def delete_webtoon(
    webtoon_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Webtoon).where(Webtoon.id == webtoon_id)
    )
    webtoon = result.scalar_one_or_none()
    
    if not webtoon:
        raise HTTPException(status_code=404, detail="Webtoon not found")
    
    await session.delete(webtoon)
    await session.commit()
    
    return {"message": "Webtoon deleted successfully"}

@app.post("/api/webtoons/{webtoon_id}/edit")
async def edit_webtoon(
    webtoon_id: int,
    edit_data: WebtoonEdit,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Webtoon).where(Webtoon.id == webtoon_id)
    )
    webtoon = result.scalar_one_or_none()
    
    if not webtoon:
        raise HTTPException(status_code=404, detail="Webtoon not found")
    
    response = {
        "status": "received",
        "webtoon_id": webtoon_id,
        "message": "편집 요청이 접수되었습니다."
    }
    
    if edit_data.drawing:
        response["drawing_status"] = "그림 편집 기능 준비 중"
    
    if edit_data.llm_question:
        response["llm_response"] = f"'{edit_data.llm_question}'에 대한 LLM 응답 기능 준비 중"
    
    # Increase view count
    webtoon.view_count += 1
    await session.commit()
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)