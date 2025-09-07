"""
Webtoons router (No Auth Version)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Request, Response
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os
import uuid
from PIL import Image
import io

from database import get_db
from models import Webtoon, Scene, Character, Like
from schemas import (
    WebtoonCreate, WebtoonUpdate, WebtoonResponse, WebtoonListResponse,
    CharacterCreate, CharacterResponse, CharacterUpdate,
    PaginationParams
)
from session import get_or_create_session_id, get_session_id, check_ownership

router = APIRouter()

@router.get("/", response_model=WebtoonListResponse)
async def get_webtoons(
    request: Request,
    response: Response,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of webtoons with pagination"""
    session_id = get_or_create_session_id(request, response)
    
    query = db.query(Webtoon)
    
    if status:
        query = query.filter(Webtoon.status == status)
    if genre:
        query = query.filter(Webtoon.genre == genre)
    
    # Show only published webtoons or user's own webtoons
    query = query.filter(
        (Webtoon.status == "published") | (Webtoon.session_id == session_id)
    )
    
    total = query.count()
    webtoons = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Add ownership and like status
    webtoon_responses = []
    for webtoon in webtoons:
        webtoon_dict = webtoon.__dict__
        webtoon_dict['is_owner'] = check_ownership(session_id, webtoon.session_id)
        
        # Check if liked
        like = db.query(Like).filter(
            Like.webtoon_id == webtoon.id,
            Like.session_id == session_id
        ).first()
        webtoon_dict['is_liked'] = like is not None
        
        webtoon_responses.append(WebtoonResponse(**webtoon_dict))
    
    return {
        "webtoons": webtoon_responses,
        "total": total,
        "page": page,
        "per_page": per_page
    }

@router.get("/my", response_model=List[WebtoonResponse])
async def get_my_webtoons(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Get current session's webtoons"""
    session_id = get_or_create_session_id(request, response)
    
    webtoons = db.query(Webtoon).filter(
        Webtoon.session_id == session_id
    ).all()
    
    # Add ownership flag
    webtoon_responses = []
    for webtoon in webtoons:
        webtoon_dict = webtoon.__dict__
        webtoon_dict['is_owner'] = True
        webtoon_dict['is_liked'] = False
        webtoon_responses.append(WebtoonResponse(**webtoon_dict))
    
    return webtoon_responses

@router.get("/{webtoon_id}", response_model=WebtoonResponse)
async def get_webtoon(
    webtoon_id: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Get a specific webtoon"""
    session_id = get_or_create_session_id(request, response)
    
    webtoon = db.query(Webtoon).filter(Webtoon.id == webtoon_id).first()
    
    if not webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    # Increment view count
    webtoon.view_count += 1
    db.commit()
    
    # Prepare response
    webtoon_dict = webtoon.__dict__
    webtoon_dict['is_owner'] = check_ownership(session_id, webtoon.session_id)
    
    # Check if liked
    like = db.query(Like).filter(
        Like.webtoon_id == webtoon.id,
        Like.session_id == session_id
    ).first()
    webtoon_dict['is_liked'] = like is not None
    
    return WebtoonResponse(**webtoon_dict)

@router.post("/", response_model=WebtoonResponse)
async def create_webtoon(
    webtoon: WebtoonCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Create a new webtoon"""
    session_id = get_or_create_session_id(request, response)
    
    db_webtoon = Webtoon(
        **webtoon.dict(exclude={'session_id'}),
        session_id=session_id,
        status="published"
    )
    db.add(db_webtoon)
    db.commit()
    db.refresh(db_webtoon)
    
    # Prepare response
    webtoon_dict = db_webtoon.__dict__
    webtoon_dict['is_owner'] = True
    webtoon_dict['is_liked'] = False
    
    return WebtoonResponse(**webtoon_dict)

@router.put("/{webtoon_id}", response_model=WebtoonResponse)
async def update_webtoon(
    webtoon_id: str,
    webtoon_update: WebtoonUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Update a webtoon"""
    session_id = get_or_create_session_id(request, response)
    
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == webtoon_id).first()
    
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    # Check ownership
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this webtoon"
        )
    
    # Update fields
    update_data = webtoon_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_webtoon, field, value)
    
    db.commit()
    db.refresh(db_webtoon)
    
    # Prepare response
    webtoon_dict = db_webtoon.__dict__
    webtoon_dict['is_owner'] = True
    
    # Check if liked
    like = db.query(Like).filter(
        Like.webtoon_id == webtoon_id,
        Like.session_id == session_id
    ).first()
    webtoon_dict['is_liked'] = like is not None
    
    return WebtoonResponse(**webtoon_dict)

@router.delete("/{webtoon_id}")
async def delete_webtoon(
    webtoon_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a webtoon"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == webtoon_id).first()
    
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    # Check ownership
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this webtoon"
        )
    
    db.delete(db_webtoon)
    db.commit()
    
    return {"message": "Webtoon deleted successfully"}

@router.post("/{webtoon_id}/thumbnail")
async def upload_thumbnail(
    webtoon_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload thumbnail for a webtoon"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == webtoon_id).first()
    
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    # Check ownership
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this webtoon"
        )
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"static/uploads/thumbnails/{unique_filename}"
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save and resize image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Resize to thumbnail size (400x600 for webtoon thumbnail)
    image.thumbnail((400, 600), Image.Resampling.LANCZOS)
    image.save(file_path)
    
    # Update webtoon thumbnail URL
    db_webtoon.thumbnail_url = f"/static/uploads/thumbnails/{unique_filename}"
    db.commit()
    
    return {"thumbnail_url": db_webtoon.thumbnail_url}

# Character endpoints
@router.get("/{webtoon_id}/characters", response_model=List[CharacterResponse])
async def get_webtoon_characters(
    webtoon_id: str,
    db: Session = Depends(get_db)
):
    """Get characters of a webtoon"""
    characters = db.query(Character).filter(
        Character.webtoon_id == webtoon_id
    ).all()
    
    return characters

@router.post("/{webtoon_id}/characters", response_model=CharacterResponse)
async def create_character(
    webtoon_id: str,
    character: CharacterCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a character for a webtoon"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Check webtoon exists and user owns it
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == webtoon_id).first()
    
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add characters to this webtoon"
        )
    
    db_character = Character(
        **character.dict(),
        webtoon_id=webtoon_id
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    
    return db_character

@router.put("/{webtoon_id}/characters/{character_id}", response_model=CharacterResponse)
async def update_character(
    webtoon_id: str,
    character_id: str,
    character_update: CharacterUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a character"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Check character exists
    db_character = db.query(Character).filter(
        Character.id == character_id,
        Character.webtoon_id == webtoon_id
    ).first()
    
    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this character"
        )
    
    # Update fields
    update_data = character_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_character, field, value)
    
    db.commit()
    db.refresh(db_character)
    
    return db_character