"""
Episodes router (No Auth Version)
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid

from database import get_db
from models import Episode, Webtoon, EditHistory
from schemas import (
    EpisodeCreate, EpisodeUpdate, EpisodeResponse,
    EditHistoryCreate, EditHistoryResponse
)
from session import get_session_id, check_ownership

router = APIRouter()

@router.get("/webtoon/{webtoon_id}", response_model=List[EpisodeResponse])
async def get_webtoon_episodes(
    webtoon_id: int,
    episode_number: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get episodes of a webtoon"""
    query = db.query(Episode).filter(Episode.webtoon_id == webtoon_id)
    
    if episode_number is not None:
        query = query.filter(Episode.episode_number == episode_number)
    
    episodes = query.order_by(
        Episode.episode_number,
        Episode.scene_order
    ).all()
    
    return episodes

@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific episode"""
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    return episode

@router.post("/", response_model=EpisodeResponse)
async def create_episode(
    episode: EpisodeCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new episode"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Check webtoon exists and user owns it
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == episode.webtoon_id).first()
    
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add episodes to this webtoon"
        )
    
    db_episode = Episode(**episode.dict())
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    
    return db_episode

@router.put("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_id: int,
    episode_update: EpisodeUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update an episode"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_episode.webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this episode"
        )
    
    # Save original content for edit history
    original_content = {
        "title": db_episode.title,
        "dialogue": db_episode.dialogue,
        "description": db_episode.description,
        "narration": db_episode.narration,
        "image_url": db_episode.image_url,
        "character_positions": db_episode.character_positions,
        "panel_layout": db_episode.panel_layout
    }
    
    # Update fields
    update_data = episode_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_episode, field, value)
    
    # Create edit history
    edit_history = EditHistory(
        episode_id=episode_id,
        session_id=session_id,
        edit_type="manual",
        original_content=original_content,
        edited_content=update_data
    )
    db.add(edit_history)
    
    db.commit()
    db.refresh(db_episode)
    
    return db_episode

@router.delete("/{episode_id}")
async def delete_episode(
    episode_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete an episode"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_episode.webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this episode"
        )
    
    db.delete(db_episode)
    db.commit()
    
    return {"message": "Episode deleted successfully"}

@router.post("/{episode_id}/image")
async def upload_episode_image(
    episode_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload image for an episode"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_episode.webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this episode"
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
    file_path = f"static/uploads/episodes/{unique_filename}"
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save image
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update episode image URL
    db_episode.image_url = f"/static/uploads/episodes/{unique_filename}"
    db.commit()
    
    return {"image_url": db_episode.image_url}

@router.post("/batch", response_model=List[EpisodeResponse])
async def create_episodes_batch(
    episodes: List[EpisodeCreate],
    request: Request,
    db: Session = Depends(get_db)
):
    """Create multiple episodes at once"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    if not episodes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No episodes provided"
        )
    
    # Check all episodes are for the same webtoon
    webtoon_id = episodes[0].webtoon_id
    if not all(ep.webtoon_id == webtoon_id for ep in episodes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All episodes must be for the same webtoon"
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
            detail="Not authorized to add episodes to this webtoon"
        )
    
    # Create all episodes
    db_episodes = []
    for episode in episodes:
        db_episode = Episode(**episode.dict())
        db.add(db_episode)
        db_episodes.append(db_episode)
    
    db.commit()
    
    # Refresh all episodes
    for db_episode in db_episodes:
        db.refresh(db_episode)
    
    return db_episodes

@router.get("/{episode_id}/history", response_model=List[EditHistoryResponse])
async def get_episode_edit_history(
    episode_id: int,
    db: Session = Depends(get_db)
):
    """Get edit history of an episode"""
    history = db.query(EditHistory).filter(
        EditHistory.episode_id == episode_id
    ).order_by(EditHistory.created_at.desc()).all()
    
    return history