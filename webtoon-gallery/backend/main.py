from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os
import random
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager
from bson import ObjectId

from database import connect_to_mongo, close_mongo_connection, get_database
from models import (
    Webtoon, WebtoonCreate, WebtoonUpdate, WebtoonEdit,
    PaginatedWebtoons, Episode, Character, WebtoonImage, 
    StoryboardPanel, ImageType
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await initialize_sample_data()
    yield
    await close_mongo_connection()

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

async def initialize_sample_data():
    """MongoDB에 샘플 데이터가 없으면 생성"""
    db = get_database()
    count = await db.webtoons.count_documents({})
    
    if count == 0:
        print("Initializing sample data...")
        webtoons = generate_sample_webtoons()
        await db.webtoons.insert_many([w.dict(exclude={"id"}) for w in webtoons])
        print(f"Created {len(webtoons)} sample webtoons")

def generate_sample_webtoons():
    """100개의 샘플 웹툰 데이터 생성"""
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
    
    webtoons = []
    for i in range(1, 101):
        thumbnail_index = ((i - 1) % 3) + 1
        num_episodes = random.randint(1, 5)
        
        episodes = []
        all_images = []
        
        for ep_num in range(1, num_episodes + 1):
            num_images = random.randint(4, 5)
            episode_images = []
            storyboard = []
            
            for img_num in range(1, num_images + 1):
                image_url = f"/static/images/webtoon{thumbnail_index}/ep1_{img_num}.jpg"
                episode_images.append(image_url)
                
                # 스토리보드 패널 생성
                panel = StoryboardPanel(
                    panel_number=img_num,
                    description=f"장면 {img_num}: 캐릭터가 등장하여 이야기를 전개",
                    dialogue=f"대사 {img_num}" if random.choice([True, False]) else None,
                    camera_angle=random.choice(["클로즈업", "미디엄샷", "롱샷", "버드아이뷰"]),
                    scene_prompt=f"웹툰 스타일, 에피소드 {ep_num} 장면 {img_num}"
                )
                storyboard.append(panel)
                
                # 웹툰 이미지 정보 생성
                webtoon_image = WebtoonImage(
                    url=image_url,
                    type=ImageType.EPISODE,
                    episode=ep_num,
                    panel_number=img_num,
                    generation_prompt=f"{random.choice(style_prompts)}, 에피소드 {ep_num} 컷 {img_num}",
                    generated_at=datetime.utcnow()
                )
                all_images.append(webtoon_image)
            
            episode = Episode(
                episode_number=ep_num,
                title=f"에피소드 {ep_num}: {random.choice(titles_prefix)} {random.choice(titles_suffix)}",
                images=episode_images,
                storyboard=storyboard,
                created_at=datetime.utcnow()
            )
            episodes.append(episode)
        
        # 썸네일 이미지 추가
        thumbnail_url = f"/static/images/webtoon{thumbnail_index}/ep1_1.jpg"
        all_images.insert(0, WebtoonImage(
            url=thumbnail_url,
            type=ImageType.THUMBNAIL,
            generation_prompt=f"썸네일 이미지, {random.choice(style_prompts)}",
            generated_at=datetime.utcnow()
        ))
        
        # 캐릭터 생성
        characters = []
        for char_idx, char_name in enumerate(random.sample(character_names, min(3, len(character_names)))):
            character = Character(
                name=f"{char_name} {i}-{char_idx}",
                description=f"웹툰 {i}의 {char_name} 캐릭터",
                design_prompt=f"{char_name} 캐릭터, {random.choice(style_prompts)}",
                reference_images=[f"/static/images/webtoon{thumbnail_index}/ep1_1.jpg"]
            )
            characters.append(character)
        
        selected_genres = random.sample(genres, random.randint(1, 3))
        
        webtoon = Webtoon(
            title=f"{random.choice(titles_prefix)} {random.choice(titles_suffix)} {i}",
            description=f"웹툰 {i}번의 흥미진진한 이야기. {', '.join(selected_genres)} 장르의 대표작으로 독자들에게 사랑받는 작품입니다.",
            genre=selected_genres,
            author=f"작가{chr(65 + (i % 26))}",
            thumbnail=thumbnail_url,
            episodes=episodes,
            total_episodes=len(episodes),
            characters=characters,
            world_setting=f"웹툰 {i}의 세계관: {random.choice(['현대', '판타지', '미래', '과거', '이세계'])} 배경",
            main_prompt=f"웹툰 {i}: {random.choice(titles_prefix)} {random.choice(titles_suffix)}의 메인 스토리",
            style_prompt=random.choice(style_prompts),
            all_images=all_images,
            tags=[f"태그{j}" for j in range(1, random.randint(3, 6))],
            status=random.choice(["ongoing", "completed", "hiatus"]),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            view_count=random.randint(100, 10000),
            like_count=random.randint(10, 1000)
        )
        webtoons.append(webtoon)
    
    return webtoons

@app.get("/")
def read_root():
    return {"message": "Webtoon Gallery API with MongoDB"}

@app.get("/api/webtoons", response_model=PaginatedWebtoons)
async def get_webtoons(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    genre: Optional[str] = None,
    status: Optional[str] = None
):
    db = get_database()
    
    # 필터 구성
    filter_query = {}
    if genre:
        filter_query["genre"] = {"$in": [genre]}
    if status:
        filter_query["status"] = status
    
    # 전체 개수 조회
    total = await db.webtoons.count_documents(filter_query)
    
    # 페이지네이션
    skip = (page - 1) * per_page
    
    # 웹툰 조회
    cursor = db.webtoons.find(filter_query).skip(skip).limit(per_page)
    webtoons = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        webtoons.append(Webtoon(**doc))
    
    has_more = skip + per_page < total
    
    return PaginatedWebtoons(
        items=webtoons,
        total=total,
        page=page,
        per_page=per_page,
        has_more=has_more
    )

@app.get("/api/webtoons/{webtoon_id}", response_model=Webtoon)
async def get_webtoon(webtoon_id: str):
    db = get_database()
    
    try:
        doc = await db.webtoons.find_one({"_id": ObjectId(webtoon_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Webtoon not found")
        
        doc["_id"] = str(doc["_id"])
        return Webtoon(**doc)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid webtoon ID")

@app.post("/api/webtoons", response_model=Webtoon)
async def create_webtoon(webtoon: WebtoonCreate):
    db = get_database()
    
    new_webtoon = Webtoon(
        **webtoon.dict(),
        episodes=[],
        total_episodes=0,
        characters=[],
        all_images=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        view_count=0,
        like_count=0
    )
    
    result = await db.webtoons.insert_one(new_webtoon.dict(exclude={"id"}))
    created = await db.webtoons.find_one({"_id": result.inserted_id})
    created["_id"] = str(created["_id"])
    
    return Webtoon(**created)

@app.put("/api/webtoons/{webtoon_id}", response_model=Webtoon)
async def update_webtoon(webtoon_id: str, update: WebtoonUpdate):
    db = get_database()
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        result = await db.webtoons.update_one(
            {"_id": ObjectId(webtoon_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Webtoon not found")
        
        updated = await db.webtoons.find_one({"_id": ObjectId(webtoon_id)})
        updated["_id"] = str(updated["_id"])
        
        return Webtoon(**updated)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid webtoon ID")

@app.delete("/api/webtoons/{webtoon_id}")
async def delete_webtoon(webtoon_id: str):
    db = get_database()
    
    try:
        result = await db.webtoons.delete_one({"_id": ObjectId(webtoon_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Webtoon not found")
        
        return {"message": "Webtoon deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid webtoon ID")

@app.post("/api/webtoons/{webtoon_id}/edit")
async def edit_webtoon(webtoon_id: str, edit: WebtoonEdit):
    db = get_database()
    
    try:
        webtoon = await db.webtoons.find_one({"_id": ObjectId(webtoon_id)})
        if not webtoon:
            raise HTTPException(status_code=404, detail="Webtoon not found")
        
        response = {
            "status": "received",
            "webtoon_id": webtoon_id,
            "message": "편집 요청이 접수되었습니다."
        }
        
        if edit.drawing:
            response["drawing_status"] = "그림 편집 기능 준비 중"
        
        if edit.llm_question:
            response["llm_response"] = f"'{edit.llm_question}'에 대한 LLM 응답 기능 준비 중"
        
        # 조회수 증가
        await db.webtoons.update_one(
            {"_id": ObjectId(webtoon_id)},
            {"$inc": {"view_count": 1}}
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid webtoon ID")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)