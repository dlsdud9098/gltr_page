"""
Scenes router (Updated for Text2Cuts)
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os
import uuid

from database import get_db
from models import Scene, Dialogue, Webtoon, EditHistory
from schemas import (
    SceneCreate, SceneUpdate, SceneResponse,
    DialogueCreate, DialogueUpdate, DialogueResponse,
    EditHistoryCreate, EditHistoryResponse
)
from session import get_session_id, check_ownership

router = APIRouter()

@router.get("/webtoon/{webtoon_id}", response_model=List[SceneResponse])
async def get_webtoon_scenes(
    webtoon_id: int,
    db: Session = Depends(get_db)
):
    """Get scenes of a webtoon with dialogues"""
    scenes = db.query(Scene).options(
        joinedload(Scene.dialogues)
    ).filter(
        Scene.webtoon_id == webtoon_id
    ).order_by(
        Scene.scene_number
    ).all()
    
    return scenes

@router.get("/{scene_id}", response_model=SceneResponse)
async def get_scene(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific scene with dialogues"""
    scene = db.query(Scene).options(
        joinedload(Scene.dialogues)
    ).filter(Scene.id == scene_id).first()
    
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    return scene

@router.post("/", response_model=SceneResponse)
async def create_scene(
    scene: SceneCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new scene"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Check webtoon exists and user owns it
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == scene.webtoon_id).first()
    
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add scenes to this webtoon"
        )
    
    db_scene = Scene(**scene.dict())
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    
    return db_scene

@router.put("/{scene_id}", response_model=SceneResponse)
async def update_scene(
    scene_id: int,
    scene_update: SceneUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a scene"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
    
    if not db_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_scene.webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this scene"
        )
    
    # Save original content for edit history
    original_content = {
        "scene_description": db_scene.scene_description,
        "narration": db_scene.narration,
        "image_url": db_scene.image_url,
        "character_positions": db_scene.character_positions,
        "panel_layout": db_scene.panel_layout
    }
    
    # Update fields
    update_data = scene_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_scene, field, value)
    
    # Create edit history
    edit_history = EditHistory(
        scene_id=scene_id,
        session_id=session_id,
        edit_type="manual",
        original_content=original_content,
        edited_content=update_data
    )
    db.add(edit_history)
    
    db.commit()
    db.refresh(db_scene)
    
    return db_scene

@router.delete("/{scene_id}")
async def delete_scene(
    scene_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a scene"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
    
    if not db_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_scene.webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this scene"
        )
    
    db.delete(db_scene)
    db.commit()
    
    return {"message": "Scene deleted successfully"}

# Dialogue endpoints
@router.post("/{scene_id}/dialogues", response_model=DialogueResponse)
async def create_dialogue(
    scene_id: int,
    dialogue: DialogueCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Add a dialogue to a scene"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Check scene exists
    db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
    
    if not db_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_scene.webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add dialogues to this scene"
        )
    
    # Create dialogue
    dialogue_data = dialogue.dict()
    dialogue_data['scene_id'] = scene_id
    db_dialogue = Dialogue(**dialogue_data)
    db.add(db_dialogue)
    db.commit()
    db.refresh(db_dialogue)
    
    return db_dialogue

@router.put("/dialogues/{dialogue_id}", response_model=DialogueResponse)
async def update_dialogue(
    dialogue_id: int,
    dialogue_update: DialogueUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a dialogue"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not db_dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dialogue not found"
        )
    
    # Check ownership through scene
    db_scene = db.query(Scene).filter(Scene.id == db_dialogue.scene_id).first()
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_scene.webtoon_id).first()
    
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this dialogue"
        )
    
    # Update fields
    update_data = dialogue_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dialogue, field, value)
    
    db.commit()
    db.refresh(db_dialogue)
    
    return db_dialogue

@router.delete("/dialogues/{dialogue_id}")
async def delete_dialogue(
    dialogue_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a dialogue"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not db_dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dialogue not found"
        )
    
    # Check ownership through scene
    db_scene = db.query(Scene).filter(Scene.id == db_dialogue.scene_id).first()
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_scene.webtoon_id).first()
    
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this dialogue"
        )
    
    db.delete(db_dialogue)
    db.commit()
    
    return {"message": "Dialogue deleted successfully"}

@router.post("/{scene_id}/image")
async def upload_scene_image(
    scene_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload image for a scene"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_scene = db.query(Scene).filter(Scene.id == scene_id).first()
    
    if not db_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    # Check ownership
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == db_scene.webtoon_id).first()
    if not check_ownership(session_id, db_webtoon.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this scene"
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
    file_path = f"static/uploads/scenes/{unique_filename}"
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save image
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update scene image URL
    db_scene.image_url = f"/static/uploads/scenes/{unique_filename}"
    db.commit()
    
    return {"image_url": db_scene.image_url}

@router.post("/batch", response_model=List[SceneResponse])
async def create_scenes_batch(
    scenes: List[SceneCreate],
    request: Request,
    db: Session = Depends(get_db)
):
    """Create multiple scenes at once"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    if not scenes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No scenes provided"
        )
    
    # Check all scenes are for the same webtoon
    webtoon_id = scenes[0].webtoon_id
    if not all(sc.webtoon_id == webtoon_id for sc in scenes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All scenes must be for the same webtoon"
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
            detail="Not authorized to add scenes to this webtoon"
        )
    
    # Create all scenes
    db_scenes = []
    for scene in scenes:
        db_scene = Scene(**scene.dict())
        db.add(db_scene)
        db_scenes.append(db_scene)
    
    db.commit()
    
    # Refresh all scenes
    for db_scene in db_scenes:
        db.refresh(db_scene)
    
    return db_scenes

@router.get("/{scene_id}/history", response_model=List[EditHistoryResponse])
async def get_scene_edit_history(
    scene_id: int,
    db: Session = Depends(get_db)
):
    """Get edit history of a scene"""
    history = db.query(EditHistory).filter(
        EditHistory.scene_id == scene_id
    ).order_by(EditHistory.created_at.desc()).all()
    
    return history