# MyriadStar (中心化阶段)

“Be Your Star. Shine Your Expertise.” —— MyriadStar 旨在让每位用户拥有一颗可成长、可验证的智星，通过持续反馈与强化学习不断提升专业光芒。

## 当前内容

- `docs/api-design.md`：GraphQL + REST API 设计
- `docs/database-schema.md`：关系型/非结构化/向量/对象存储规划
- `docs/scaffolding.md`：工程脚手架与依赖说明
- `apps/`：保留 API、Web、Mobile 目录
- `packages/shared`：预留跨端共享代码位置
- `infra/`：后续放置 docker-compose 与 IaC

## 快速开始（规划）

1. 准备 `.env`（密钥、数据库连接）。
2. 启动依赖：`docker compose up -d`（PostgreSQL、MongoDB、Redis、Milvus、MinIO）。
3. API：`cd apps/api && uv run fastapi dev`。
4. Web：`cd apps/web && pnpm dev`。
5. Mobile：`cd apps/mobile && pnpm expo start`。

## 里程碑

详见 `docs/scaffolding.md` 中的路线图，当前阶段聚焦：
- 定义核心数据模型与 API
- 搭建基础服务脚手架
- 准备 RL 与评估流水线的本地验证

## 贡献

1. fork & clone 仓库
2. 创建 feature 分支
3. `pnpm lint` / `uv run pytest`
4. 提交 PR 并描述变更与测试

