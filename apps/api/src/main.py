from fastapi import Depends, FastAPI
from sqlmodel import Session, select
from strawberry.fastapi import GraphQLRouter

from config import get_settings
from db import get_session, init_db
from models import MagnitudeHistory, Skill, Star, StarTrial, User
from routes_agent import router as agent_router
from routes_community import router as community_router
from routes_evaluator import router as evaluator_router
from routes_knowledge import router as knowledge_router
from routes_skills import router as skills_router

settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def build_graphql_router() -> GraphQLRouter:
    import strawberry

    @strawberry.type
    class GQLUser:
        id: str
        email: str
        display_name: str | None

    @strawberry.type
    class GQLStar:
        id: str
        name: str
        domain: str
        owner_id: str

        @strawberry.field
        def latest_magnitude(self, info) -> str | None:  # type: ignore[override]
            session: Session = info.context["session"]
            record = (
                session.exec(
                    select(MagnitudeHistory)
                    .where(MagnitudeHistory.star_id == self.id)  # type: ignore[arg-type]
                    .order_by(MagnitudeHistory.evaluated_at.desc()),
                )
                .first()
            )
            return record.level if record else None

    @strawberry.type
    class Query:
        @strawberry.field
        def health(self) -> str:
            return "stellar"

        @strawberry.field
        def me(self, info) -> GQLUser | None:  # type: ignore[override]
            # PoC：先返回或创建一个默认用户，后续接入真实 Auth
            session: Session = info.context["session"]
            user = session.exec(select(User).limit(1)).first()
            if not user:
                user = User(email="founder@mystar.local", display_name="首位星主")
                session.add(user)
                session.commit()
                session.refresh(user)
            return GQLUser(
                id=str(user.id),
                email=user.email,
                display_name=user.display_name,
            )

        @strawberry.field
        def stars(self, info) -> list[GQLStar]:  # type: ignore[override]
            session: Session = info.context["session"]
            stars = session.exec(select(Star)).all()
            return [
                GQLStar(
                    id=str(s.id),
                    name=s.name,
                    domain=s.domain,
                    owner_id=str(s.owner_id),
                )
                for s in stars
            ]

        @strawberry.field
        def trials(self, info) -> list[str]:  # type: ignore[override]
            """返回所有星试标题，最小可见化."""

            session: Session = info.context["session"]
            trials = session.exec(select(StarTrial)).all()
            return [t.title for t in trials]

        @strawberry.field
        def skills(self, info) -> list[str]:  # type: ignore[override]
            """返回已注册星技名称列表."""

            session: Session = info.context["session"]
            skills = session.exec(select(Skill)).all()
            return [s.name for s in skills]

    @strawberry.type
    class Mutation:
        @strawberry.mutation
        def create_star(self, info, name: str, domain: str) -> GQLStar:  # type: ignore[override]
            session: Session = info.context["session"]
            user = session.exec(select(User).limit(1)).first()
            if not user:
                user = User(email="founder@mystar.local", display_name="首位星主")
                session.add(user)
                session.commit()
                session.refresh(user)
            star = Star(name=name, domain=domain, owner_id=user.id)
            session.add(star)
            session.commit()
            session.refresh(star)
            return GQLStar(id=str(star.id), name=star.name, domain=star.domain, owner_id=str(star.owner_id))

        @strawberry.mutation
        def ingest_knowledge(self, info, star_id: str) -> bool:  # type: ignore[override]
            """占位 GraphQL Mutation：内部转到 REST /knowledge/v1/uploads。

            目前仅在数据库中记录一条知识任务，不做真实向量化。
            """

            from uuid import UUID

            from models import KnowledgeTask

            session: Session = info.context["session"]
            task = KnowledgeTask(star_id=UUID(star_id), source_type="graphql", status="completed")
            session.add(task)
            session.commit()
            return True

        @strawberry.mutation
        def evaluate_star(self, info, star_id: str) -> str:  # type: ignore[override]
            """占位 GraphQL Mutation：根据星尘数量给星等。"""

            from uuid import UUID

            session: Session = info.context["session"]
            # 直接调用 Evaluator 的核心逻辑：这里简单起见，重复一遍映射规则
            from models import KnowledgeTask as KT

            task_count = session.exec(
                select(KT).where(KT.star_id == UUID(star_id)),
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

            record = MagnitudeHistory(star_id=UUID(star_id), overall=overall, level=level)
            session.add(record)
            session.commit()
            return level

        @strawberry.mutation
        def create_trial(self, info, title: str, prompt: str) -> bool:  # type: ignore[override]
            """通过 GraphQL 创建一条星试记录."""

            session: Session = info.context["session"]
            trial = StarTrial(title=title, prompt=prompt, status="ongoing")
            session.add(trial)
            session.commit()
            return True

        @strawberry.mutation
        def register_skill(self, info, name: str, description: str | None = None) -> bool:  # type: ignore[override]
            """通过 GraphQL 注册一个简单星技."""

            session: Session = info.context["session"]
            skill = Skill(name=name, description=description, status="published")
            session.add(skill)
            session.commit()
            return True

    schema = strawberry.Schema(query=Query, mutation=Mutation)

    def get_context(session: Session = Depends(get_session)):
        return {"session": session}

    return GraphQLRouter(schema, path="/graphql", context_getter=get_context)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.environment}


app.include_router(build_graphql_router(), include_in_schema=False)
app.include_router(agent_router)
app.include_router(knowledge_router)
app.include_router(evaluator_router)
app.include_router(community_router)
app.include_router(skills_router)
