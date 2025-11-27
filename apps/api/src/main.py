from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)


def build_graphql_router() -> GraphQLRouter:
    import strawberry

    @strawberry.type
    class Query:
        @strawberry.field
        def health(self) -> str:
            return "stellar"

    schema = strawberry.Schema(query=Query)
    return GraphQLRouter(schema, path="/graphql")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.environment}


app.include_router(build_graphql_router(), include_in_schema=False)
