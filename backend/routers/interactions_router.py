"""
User interactions router (No Auth Version)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Like, Webtoon, Comment
from schemas import (
    LikeCreate, LikeResponse,
    CommentCreate, CommentUpdate, CommentResponse
)
from session import get_or_create_session_id, get_session_id, check_ownership

router = APIRouter()

@router.post("/like", response_model=LikeResponse)
async def toggle_like(
    webtoon_id: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Toggle like for a webtoon"""
    session_id = get_or_create_session_id(request, response)
    
    # Check if webtoon exists
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == webtoon_id).first()
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.webtoon_id == webtoon_id,
        Like.session_id == session_id
    ).first()
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        if db_webtoon.like_count > 0:
            db_webtoon.like_count -= 1
        db.commit()
        return {"message": "Unliked", "liked": False}
    else:
        # Like
        new_like = Like(
            webtoon_id=webtoon_id,
            session_id=session_id
        )
        db.add(new_like)
        db_webtoon.like_count += 1
        db.commit()
        db.refresh(new_like)
        return {"message": "Liked", "liked": True, **new_like.__dict__}

@router.get("/likes", response_model=List[LikeResponse])
async def get_my_likes(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Get current session's likes"""
    session_id = get_or_create_session_id(request, response)
    
    likes = db.query(Like).filter(
        Like.session_id == session_id
    ).all()
    
    return likes

# Comment endpoints
@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Create a comment"""
    session_id = get_or_create_session_id(request, response)
    
    # Check if webtoon exists
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == comment.webtoon_id).first()
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    db_comment = Comment(
        **comment.dict(exclude={'session_id'}),
        session_id=session_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Add ownership flag
    comment_dict = db_comment.__dict__
    comment_dict['is_owner'] = True
    
    return CommentResponse(**comment_dict)

@router.get("/comments/webtoon/{webtoon_id}", response_model=List[CommentResponse])
async def get_webtoon_comments(
    webtoon_id: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Get comments for a webtoon"""
    session_id = get_or_create_session_id(request, response)
    
    comments = db.query(Comment).filter(
        Comment.webtoon_id == webtoon_id,
        Comment.parent_comment_id == None
    ).order_by(Comment.created_at.desc()).all()
    
    # Add ownership flags
    comment_responses = []
    for comment in comments:
        comment_dict = comment.__dict__
        comment_dict['is_owner'] = check_ownership(session_id, comment.session_id)
        comment_dict['replies'] = []
        
        # Get replies
        replies = db.query(Comment).filter(
            Comment.parent_comment_id == comment.id
        ).order_by(Comment.created_at).all()
        
        for reply in replies:
            reply_dict = reply.__dict__
            reply_dict['is_owner'] = check_ownership(session_id, reply.session_id)
            comment_dict['replies'].append(CommentResponse(**reply_dict))
        
        comment_responses.append(CommentResponse(**comment_dict))
    
    return comment_responses

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a comment"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check ownership
    if not check_ownership(session_id, db_comment.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )
    
    db_comment.content = comment_update.content
    db.commit()
    db.refresh(db_comment)
    
    # Add ownership flag
    comment_dict = db_comment.__dict__
    comment_dict['is_owner'] = True
    comment_dict['replies'] = []
    
    return CommentResponse(**comment_dict)

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a comment"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check ownership
    if not check_ownership(session_id, db_comment.session_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    db.delete(db_comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}