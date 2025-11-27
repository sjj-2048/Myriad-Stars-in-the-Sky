# 工程脚手架说明

## 总览

```
mystar/
├── apps/
│   ├── api/          # FastAPI 服务（GraphQL Gateway+REST）
│   ├── web/          # Next.js 前端
│   └── mobile/       # React Native / Expo 客户端
├── packages/
│   └── shared/       # 通用工具（ts/py sdk、proto、schema）
├── docs/             # 架构、API、数据文档
├── infra/            # IaC、docker-compose、监控配置
├── scripts/          # 运维/训练脚本
└── README.md
```

## 技术栈与依赖

- Node 20 + pnpm
- Python 3.11 + uv/poetry（任选，这里示例用 `uv`）
- FastAPI + Strawberry GraphQL + SQLModel + Celery
- Next.js 15 + App Router + tRPC/SWR
- React Native Expo（管理 `env` 通过 `.env.*`）
- Docker Compose：PostgreSQL、MongoDB、Milvus、MinIO、Redis、Ray

## 本地开发流程

1. `cp .env.example .env` 并填充密钥。
2. `docker compose up -d db redis mongo minio milvus` 启动依赖。
3. 安装工具链：`pnpm install`、`uv sync`。
4. `pnpm --filter web dev` 启动前端；`uv run fastapi dev` 启动 API。
5. 使用 `scripts/dev-seed.py` 写入测试数据。

## 目录细节

### `apps/api`
- `pyproject.toml`：uv/poetry 配置
- `src/main.py`：FastAPI 入口，挂载 GraphQL / REST 路由
- `src/config.py`：环境变量管理
- `src/routes/`：REST 路由（auth, stars, knowledge, agent...）
- `src/graphql/schema.py`：GraphQL 类型与 resolver
- `src/services/`：业务逻辑（trainer client、skill hub client）
- `src/events/`：Redis Stream/Kafka 消费器
- `tests/`

### `apps/web`
- `package.json` + `tsconfig.json`
- `src/app/`：App Router 页面
- `src/features/`：模块化（stars, knowledge, trials）
- `src/lib/api.ts`：调用 GraphQL client（urql/apollo）
- `src/store/`：Zustand 状态

### `apps/mobile`
- `app.json`、`package.json`
- `src/app/`：Expo Router
- `src/modules/`：复用 web 的 GraphQL 查询（通过 packages/shared）

### `packages/shared`
- `tsconfig.json`
- `src/graphql/generated.ts`：通过 `graphql-codegen` 生成
- `src/constants.ts`
- `python/` 子目录可放 pydantic schema 共享

### `infra`
- `docker-compose.yml`
- `terraform/` 或 `pulumi/` 未来云资源定义
- `grafana/`, `prometheus/` 配置

### `scripts`
- `dev-seed.py`
- `train/star_trainer.py`
- `ci/lint.sh`

## 版本管理

- GitHub 仓库：`github.com/myriadstar/core`
- 分支策略：`main`（稳定）+ `develop`（集成）+ feature branches
- CI：GitHub Actions（lint, test, build, docker push）

