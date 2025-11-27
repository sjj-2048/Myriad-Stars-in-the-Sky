from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from db import get_session
from llm import ChatMessage, generate_reply
from models import Star


router = APIRouter(prefix="/agent/v1", tags=["agent"])


class MessageIn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    star_id: UUID
    messages: List[MessageIn]


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat_with_star(payload: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    """为任意智星提供基础对话能力。

    - 查出 star；
    - 调用 LLM 抽象层生成回复；
    - 未来可在此记录对话日志并触发 RL 训练事件。
    """

    star = session.exec(select(Star).where(Star.id == payload.star_id)).first()
    if not star:
        raise HTTPException(status_code=404, detail="star not found")

    messages = [ChatMessage(role=m.role, content=m.content) for m in payload.messages]
    reply = generate_reply(star, messages)
    return ChatResponse(reply=reply)


