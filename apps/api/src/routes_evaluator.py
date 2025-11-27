from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from db import get_session
from models import KnowledgeTask, MagnitudeHistory


router = APIRouter(prefix="/evaluator/v1", tags=["evaluator"])


class EvalRequest(BaseModel):
    star_id: UUID


class EvalResponse(BaseModel):
    star_id: UUID
    overall: float
    level: str


@router.post("/run", response_model=EvalResponse)
def run_evaluation(body: EvalRequest, session: Session = Depends(get_session)) -> EvalResponse:
    """最小“评估”：根据星尘任务数量给出一个简单分数并记录一条历史。

    - 真实版本会调用自动评估脚本，对回答样本做打分；
    - 这里先用 knowledge_task 数量映射到 0-5 分，再映射到 L1-L5。
    """

    task_count = session.exec(
        select(KnowledgeTask).where(KnowledgeTask.star_id == body.star_id),
    ).count()

    overall = min(5.0, 1.0 + task_count * 0.5)
    if overall >= 4.5:
        level = "L5"
    elif overall >= 3.5:
        level = "L4"
    elif overall >= 2.5:
        level = "L3"
    elif overall >= 1.5:
        level = "L2"
    else:
        level = "L1"

    record = MagnitudeHistory(star_id=body.star_id, overall=overall, level=level)
    session.add(record)
    session.commit()

    return EvalResponse(star_id=body.star_id, overall=overall, level=level)


