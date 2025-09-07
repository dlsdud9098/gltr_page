"""
Chat router for character interactions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import random
from datetime import datetime

from database import get_db
from models import ChatMessage, Webtoon, Character, Episode
from schemas import (
    ChatMessageCreate, ChatMessageUpdate, 
    ChatMessageResponse, CharacterResponse
)
from session import get_or_create_session_id, get_session_id, check_ownership

router = APIRouter()

# Predefined AI responses for demo
AI_RESPONSES = {
    "greeting": [
        "안녕하세요! 저는 이 웹툰의 주인공입니다. 궁금한 점이 있으면 물어보세요!",
        "반가워요! 오늘은 어떤 이야기를 나누고 싶으신가요?",
        "안녕하세요! 제 이야기를 읽어주셔서 감사합니다."
    ],
    "story": [
        "이 장면에서 제가 느낀 감정은 정말 복잡했어요. 더 자세히 이야기해드릴게요.",
        "작가님이 이 부분을 그리실 때 특별히 신경 쓰신 부분이에요.",
        "이 에피소드는 제 인생의 전환점이었죠. 많은 고민 끝에 내린 결정이었어요."
    ],
    "question": [
        "흥미로운 질문이네요! 제 생각을 말씀드리자면...",
        "그 부분은 다음 에피소드에서 더 자세히 다뤄질 예정이에요!",
        "좋은 관찰이세요! 사실 그 장면에는 숨겨진 의미가 있어요."
    ],
    "general": [
        "더 자세히 알고 싶으시다면 다음 에피소드를 기대해주세요!",
        "저도 그 장면을 연기하면서 많은 생각이 들었어요.",
        "독자님의 해석이 정말 흥미롭네요! 저도 비슷한 생각을 했어요."
    ]
}

def generate_ai_response(message: str) -> str:
    """Generate AI response based on user message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["안녕", "하이", "hello", "hi"]):
        return random.choice(AI_RESPONSES["greeting"])
    elif any(word in message_lower for word in ["이야기", "스토리", "줄거리", "story"]):
        return random.choice(AI_RESPONSES["story"])
    elif "?" in message or any(word in message_lower for word in ["왜", "어떻게", "무엇", "누가"]):
        return random.choice(AI_RESPONSES["question"])
    else:
        return random.choice(AI_RESPONSES["general"])

@router.post("/chat/messages", response_model=ChatMessageResponse)
async def create_chat_message(
    message: ChatMessageCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Create a new chat message"""
    session_id = get_or_create_session_id(request, response)
    
    # Check if webtoon exists
    db_webtoon = db.query(Webtoon).filter(Webtoon.id == message.webtoon_id).first()
    if not db_webtoon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webtoon not found"
        )
    
    # Create user message
    db_message = ChatMessage(
        **message.dict(exclude={'session_id'}),
        session_id=session_id,
        is_read=True  # User's own messages are always read
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # If it's a user message, generate AI response
    if message.sender_type == "user":
        # Get main character of the webtoon
        main_character = db.query(Character).filter(
            Character.webtoon_id == message.webtoon_id,
            Character.role == "주인공"
        ).first()
        
        if not main_character:
            # Create a default character if none exists
            main_character = db.query(Character).filter(
                Character.webtoon_id == message.webtoon_id
            ).first()
        
        # Generate AI response
        ai_response_text = generate_ai_response(message.message)
        
        ai_message = ChatMessage(
            webtoon_id=message.webtoon_id,
            episode_id=message.episode_id,
            sender_type="character",
            sender_name=main_character.name if main_character else "주인공",
            message=ai_response_text,
            session_id="ai_system",
            is_read=False,  # New AI messages are unread
            character_id=main_character.id if main_character else None,
            parent_message_id=db_message.id
        )
        db.add(ai_message)
        db.commit()
    
    # Prepare response
    message_dict = db_message.__dict__
    message_dict['is_owner'] = True
    message_dict['replies'] = []
    
    return ChatMessageResponse(**message_dict)

@router.get("/chat/messages/webtoon/{webtoon_id}", response_model=List[ChatMessageResponse])
async def get_webtoon_chat_messages(
    webtoon_id: int,
    request: Request,
    response: Response,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get chat messages for a webtoon"""
    session_id = get_or_create_session_id(request, response)
    
    # Get messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.webtoon_id == webtoon_id,
        ChatMessage.parent_message_id == None
    ).order_by(ChatMessage.created_at.desc()).limit(limit).offset(offset).all()
    
    # Prepare responses with ownership flags
    message_responses = []
    for msg in messages:
        message_dict = msg.__dict__
        message_dict['is_owner'] = check_ownership(session_id, msg.session_id)
        message_dict['replies'] = []
        
        # Get character info if it's a character message
        if msg.character_id:
            character = db.query(Character).filter(Character.id == msg.character_id).first()
            if character:
                message_dict['character'] = CharacterResponse(**character.__dict__)
        
        # Get replies
        replies = db.query(ChatMessage).filter(
            ChatMessage.parent_message_id == msg.id
        ).order_by(ChatMessage.created_at).all()
        
        for reply in replies:
            reply_dict = reply.__dict__
            reply_dict['is_owner'] = check_ownership(session_id, reply.session_id)
            
            if reply.character_id:
                character = db.query(Character).filter(Character.id == reply.character_id).first()
                if character:
                    reply_dict['character'] = CharacterResponse(**character.__dict__)
            
            message_dict['replies'].append(ChatMessageResponse(**reply_dict))
        
        message_responses.append(ChatMessageResponse(**message_dict))
    
    # Reverse to show oldest first
    message_responses.reverse()
    
    return message_responses

@router.put("/chat/messages/{message_id}/read", response_model=ChatMessageResponse)
async def mark_message_as_read(
    message_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Mark a message as read"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    db_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    if not db_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Mark as read
    db_message.is_read = True
    db.commit()
    db.refresh(db_message)
    
    # Prepare response
    message_dict = db_message.__dict__
    message_dict['is_owner'] = check_ownership(session_id, db_message.session_id)
    message_dict['replies'] = []
    
    return ChatMessageResponse(**message_dict)

@router.get("/chat/unread-count/webtoon/{webtoon_id}")
async def get_unread_count(
    webtoon_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Get count of unread messages for a webtoon"""
    session_id = get_or_create_session_id(request, response)
    
    # Count unread character messages (not from the current user)
    unread_count = db.query(ChatMessage).filter(
        ChatMessage.webtoon_id == webtoon_id,
        ChatMessage.sender_type == "character",
        ChatMessage.is_read == False
    ).count()
    
    return {"unread_count": unread_count}

@router.post("/chat/messages/batch-read")
async def mark_messages_as_read(
    message_ids: List[int],
    request: Request,
    db: Session = Depends(get_db)
):
    """Mark multiple messages as read"""
    session_id = get_session_id(request)
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Update all messages
    db.query(ChatMessage).filter(
        ChatMessage.id.in_(message_ids)
    ).update({"is_read": True}, synchronize_session=False)
    
    db.commit()
    
    return {"message": "Messages marked as read", "count": len(message_ids)}