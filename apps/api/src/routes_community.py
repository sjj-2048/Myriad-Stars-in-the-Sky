from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from db import get_session
from models import StarTrial


router = APIRouter(prefix="/community/v1", tags=["community"])


class TrialCreateRequest(BaseModel):
  title: str
  prompt: str


class TrialCreateResponse(BaseModel):
  id: UUID
  title: str
  status: str


class TrialListItem(BaseModel):
  id: UUID
  title: str
  status: str


@router.post("/trials", response_model=TrialCreateResponse)
def create_trial(body: TrialCreateRequest, session: Session = Depends(get_session)) -> TrialCreateResponse:
  trial = StarTrial(title=body.title, prompt=body.prompt, status="ongoing")
  session.add(trial)
  session.commit()
  session.refresh(trial)
  return TrialCreateResponse(id=trial.id, title=trial.title, status=trial.status)


@router.get("/trials", response_model=list[TrialListItem])
def list_trials(session: Session = Depends(get_session)) -> list[TrialListItem]:
  trials = session.exec(select(StarTrial).order_by(StarTrial.created_at.desc())).all()
  return [TrialListItem(id=t.id, title=t.title, status=t.status) for t in trials]


