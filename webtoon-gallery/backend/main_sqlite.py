from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import random
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

from database import WebtoonDB
from models_simple import WebtoonSimple, PaginatedWebtoonsSimple, WebtoonEdit

app = FastAPI()

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

def generate_placeholder_image(text: str, width: int = 800, height: int = 600):
    """Generate a placeholder image with text"""
    # Create a new image with random pastel background
    colors = [
        (255, 223, 223),  # Light pink
        (223, 239, 255),  # Light blue
        (223, 255, 239),  # Light green
        (255, 239, 223),  # Light orange
        (239, 223, 255),  # Light purple
    ]
    bg_color = random.choice(colors)
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fall back to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    draw.text((text_x, text_y), text, fill=(100, 100, 100), font=font)
    
    # Add border
    draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 200, 200), width=2)
    
    return img

@app.get("/")
def root():
    return {"message": "GLTR Webtoon Gallery API (SQLite Version)"}

@app.get("/api/webtoons", response_model=PaginatedWebtoonsSimple)
async def get_webtoons(
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=50)
):
    """Get paginated webtoons from SQLite database"""
    try:
        result = WebtoonDB.get_all_webtoons(page=page, per_page=per_page)
        return result
    except Exception as e:
        print(f"Error fetching webtoons: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/webtoons/{webtoon_id}")
async def get_webtoon(webtoon_id: int):
    """Get single webtoon details"""
    try:
        webtoon = WebtoonDB.get_webtoon_by_id(webtoon_id)
        if not webtoon:
            raise HTTPException(status_code=404, detail="Webtoon not found")
        return webtoon
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching webtoon {webtoon_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/webtoons/search")
async def search_webtoons(
    q: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50)
):
    """Search webtoons by query"""
    try:
        result = WebtoonDB.search_webtoons(query=q, page=page, per_page=per_page)
        return result
    except Exception as e:
        print(f"Error searching webtoons: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webtoons/{webtoon_id}/edit")
async def edit_webtoon(webtoon_id: int, edit_request: WebtoonEdit):
    """Edit webtoon (placeholder functionality)"""
    response = {
        "message": f"웹툰 {webtoon_id} 편집 요청이 접수되었습니다.",
        "webtoon_id": webtoon_id
    }
    
    if edit_request.drawing:
        response["drawing_status"] = f"그림 편집: {edit_request.drawing[:50]}..."
    
    if edit_request.llm_question:
        # Simulate AI response
        responses = [
            "이 장면은 주인공의 감정을 잘 표현하고 있습니다.",
            "배경과 캐릭터의 조화가 훌륭합니다.",
            "스토리 전개가 자연스럽고 흥미롭습니다.",
            "색감이 웹툰의 분위기를 잘 살리고 있습니다."
        ]
        response["llm_response"] = f"AI 답변: {random.choice(responses)}"
    
    return response

@app.get("/api/images/{image_name}")
async def get_image(image_name: str):
    """Serve dynamic placeholder images"""
    # Extract information from image name
    if image_name.startswith("thumbnail_"):
        # Generate thumbnail
        webtoon_id = image_name.replace("thumbnail_", "").replace(".jpg", "")
        img = generate_placeholder_image(f"웹툰 {webtoon_id}\n썸네일", 400, 600)
    elif "scene_" in image_name:
        # Generate scene image
        parts = image_name.replace(".jpg", "").split("_")
        webtoon_id = parts[1]
        scene_num = parts[-1]
        img = generate_placeholder_image(f"웹툰 {webtoon_id}\n장면 {scene_num}", 800, 1200)
    else:
        # Default image
        img = generate_placeholder_image("웹툰 이미지", 800, 600)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return FileResponse(
        img_byte_arr,
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=3600"}
    )

@app.get("/api/stats")
async def get_stats():
    """Get database statistics"""
    try:
        from database import get_db_connection, dict_from_row
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) as count FROM webtoons")
            webtoon_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM scenes")
            scene_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM scene_characters")
            character_count = cursor.fetchone()['count']
            
            # Get theme distribution
            cursor.execute("""
                SELECT theme, COUNT(*) as count 
                FROM webtoons 
                GROUP BY theme 
                ORDER BY count DESC
            """)
            themes = [dict_from_row(row) for row in cursor.fetchall()]
            
            return {
                "total_webtoons": webtoon_count,
                "total_scenes": scene_count,
                "total_characters": character_count,
                "themes": themes
            }
    except Exception as e:
        print(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)