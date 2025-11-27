from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from db import get_session
from models import Skill


router = APIRouter(prefix="/skills/v1", tags=["skills"])


class SkillCreateRequest(BaseModel):
  name: str
  description: str | None = None
  api_endpoint: str | None = None


class SkillCreateResponse(BaseModel):
  id: UUID
  name: str
  status: str


class SkillListItem(BaseModel):
  id: UUID
  name: str
  status: str


@router.post("", response_model=SkillCreateResponse)
def register_skill(body: SkillCreateRequest, session: Session = Depends(get_session)) -> SkillCreateResponse:
  skill = Skill(name=body.name, description=body.description, api_endpoint=body.api_endpoint, status="published")
  session.add(skill)
  session.commit()
  session.refresh(skill)
  return SkillCreateResponse(id=skill.id, name=skill.name, status=skill.status)


@router.get("", response_model=list[SkillListItem])
def list_skills(session: Session = Depends(get_session)) -> list[SkillListItem]:
  skills = session.exec(select(Skill).order_by(Skill.created_at.desc())).all()
  return [SkillListItem(id=s.id, name=s.name, status=s.status) for s in skills]


