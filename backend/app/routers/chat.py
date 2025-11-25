from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models, schemas, database
from .auth import get_current_user
from ..llm.service import LLMService
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List
from sqlalchemy.orm import selectinload


limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

llm_service = LLMService()

@router.post("/sessions", response_model=schemas.ChatSession)
@limiter.limit("5/minute")
async def create_session(
    request: Request,
    request_data: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Create new session
    new_session = models.ChatSession(
        user_id=current_user.id,
        connection_id=request_data.connection_id,
        title=request_data.message[:50] # Simple title
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    # Process first message
    # 1. Save user message
    user_msg = models.ChatMessage(
        session_id=new_session.id,
        role="user",
        content=request_data.message
    )
    db.add(user_msg)
    
    # 2. Generate response
    response_data = await llm_service.generate_response(request_data.message, request_data.connection_id, db)
    
    # 3. Save assistant message
    assistant_msg = models.ChatMessage(
        session_id=new_session.id,
        role="assistant",
        content=response_data["content"],
        sql_query=response_data.get("sql_query")
    )
    db.add(assistant_msg)
    await db.commit()
    
    # Return session with messages
    # We need to refresh or re-query to get messages
    result = await db.execute(
        select(models.ChatSession)
        .where(models.ChatSession.id == new_session.id)
        .options(selectinload(models.ChatSession.messages))
    )
    return result.scalars().first()

@router.post("/sessions/{session_id}/messages", response_model=schemas.ChatMessage)
@limiter.limit("10/minute")
async def send_message(
    session_id: int,
    request: Request,
    request_data: schemas.ChatRequest, # We reuse this schema, ignoring connection_id
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Fetch session
    result = await db.execute(select(models.ChatSession).where(models.ChatSession.id == session_id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Save user message
    user_msg = models.ChatMessage(
        session_id=session_id,
        role="user",
        content=request_data.message
    )
    db.add(user_msg)
    await db.commit()
    
    # Generate response
    response_data = await llm_service.generate_response(request_data.message, session.connection_id, db)
    
    # Save assistant message
    assistant_msg = models.ChatMessage(
        session_id=session_id,
        role="assistant",
        content=response_data["content"],
        sql_query=response_data.get("sql_query")
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)
    
    return assistant_msg



@router.get("/sessions", response_model=List[schemas.ChatSession])
async def list_sessions(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(
        select(models.ChatSession)
        .where(models.ChatSession.user_id == current_user.id)
        .order_by(models.ChatSession.created_at.desc())
    )
    return result.scalars().all()

@router.get("/sessions/{session_id}", response_model=schemas.ChatSession)
async def get_session(
    session_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(
        select(models.ChatSession)
        .where(models.ChatSession.id == session_id)
        .options(selectinload(models.ChatSession.messages))
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
