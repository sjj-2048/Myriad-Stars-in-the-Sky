from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from db import get_session
from models import KnowledgeTask


router = APIRouter(prefix="/knowledge/v1", tags=["knowledge"])


class IngestRequest(BaseModel):
    star_id: UUID
    source_type: str = "upload"
    payload_uri: str | None = None


class IngestResponse(BaseModel):
    task_id: UUID
    status: str


@router.post("/uploads", response_model=IngestResponse)
def ingest_knowledge(body: IngestRequest, session: Session = Depends(get_session)) -> IngestResponse:
    """最小实现：创建一条 knowledge_task，立即标记为 completed。

    后续可以在这里：
    - 将原始内容写入 MinIO；
    - 推送向量化任务到队列；
    - 触发 RL Trainer 的事件。
    """

    task = KnowledgeTask(
        star_id=body.star_id,
        source_type=body.source_type,
        payload_uri=body.payload_uri,
        status="completed",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return IngestResponse(task_id=task.id, status=task.status)


