# MyriadStar API 设计（中心化阶段）

## 设计原则

1. **模块化**：各服务独立部署，通过 API Gateway 或 Service Mesh 暴露统一入口。
2. **双协议**：外部使用 GraphQL 聚合查询，内部服务之间保持 REST/gRPC 简洁接口。
3. **事件驱动**：关键操作（知识上传、评分、训练完成）都会发送事件到 Redis Stream/Kafka，供 RL Trainer 与 Evaluator 消费。
4. **鉴权统一**：采用 JWT（短期）+ Refresh Token，服务间使用 mTLS + 服务令牌。

---

## GraphQL Gateway（/graphql）

| Query | 描述 |
| --- | --- |
| `me` | 返回当前星主信息、拥有的智星列表 |
| `star(id)` | 查询单个智星详情（星域、星等、最近对话） |
| `stars(filter)` | 支持按星域、星等、标签搜索 |
| `starTrials(seasonId)` | 获取指定赛季题目、排名 |

| Mutation | 描述 |
| --- | --- |
| `createStar(input)` | 创建智星（名称、星域、人格设定） |
| `ingestKnowledge(input)` | 上传“星尘”任务，返回任务 ID |
| `startConversation(starId, prompt)` | 发起对话并返回流式 token id |
| `submitFeedback(conversationId, rating, comment)` | 记录偏好反馈 |
| `subscribeSkill(starId, skillId)` | 为智星安装星技 |
| `enterTrial(starId, seasonId)` | 报名星试挑战 |

> GraphQL 只做聚合/编排，实际业务调用下列 REST 服务。

---

## Auth Service（REST）

Base URL: `/auth`

| Method | Path | 说明 |
| --- | --- | --- |
| POST | `/v1/signup` | 邮箱/社媒注册，返回用户 ID + JWT |
| POST | `/v1/login` | 登录获取 Access/Refresh token |
| POST | `/v1/token/refresh` | 刷新 token |
| GET | `/v1/profile` | 获取当前用户资料、权限 |
| PATCH | `/v1/profile` | 更新昵称、头像、通知偏好 |
| POST | `/v1/api-keys` | 生成星技开发者 API Key |

---

## Star Registry Service

Base URL: `/stars`

| Method | Path | 描述 |
| --- | --- | --- |
| POST | `/v1` | 创建智星，写入 `stars` 表及默认配置 |
| GET | `/v1/:starId` | 查询智星详情、星等、能力面板 |
| PATCH | `/v1/:starId` | 更新设定（人格、边界、星域） |
| GET | `/v1/:starId/versions` | 获取星核版本列表 |
| POST | `/v1/:starId/versions/rollback` | 回滚至指定模型快照 |
| GET | `/v1/:starId/timeline` | 返回训练、评估、星试事件时间轴 |

事件：`STAR_CREATED`, `STAR_VERSION_UPDATED`, `STAR_MAGNITUDE_CHANGED`

---

## Knowledge Ingestor Service

Base URL: `/knowledge`

| Method | Path | 描述 |
| --- | --- | --- |
| POST | `/v1/uploads` | 上传文档（多部分），返回任务 ID |
| POST | `/v1/webhook` | 支持外部爬取/同步数据源回调 |
| GET | `/v1/tasks/:taskId` | 查询解析/嵌入进度 |
| POST | `/v1/tasks/:taskId/retry` | 失败任务重试 |

事件：`KNOWLEDGE_INGESTED`（携带向量索引、内容引用）

---

## Agent Core Service

Base URL: `/agent`

| Method | Path | 描述 |
| --- | --- | --- |
| POST | `/v1/session` | 创建会话（星主 <-> 智星），返回 `conversationId` |
| POST | `/v1/session/:id/message` | 发送消息，支持 `stream=true` SSE/WebSocket |
| GET | `/v1/session/:id/history` | 获取对话与上下文记忆 |
| POST | `/v1/session/:id/tools` | 注册临时工具或工作流（如星技） |

事件：`CONVERSATION_FEEDBACK`, `CONVERSATION_SUMMARY`

---

## RL Trainer Service

- 接收事件：`CONVERSATION_FEEDBACK`, `KNOWLEDGE_INGESTED`
- REST 接口：
  - `POST /trainer/v1/jobs`：手动触发训练（指定星、数据窗口、超参）
  - `GET /trainer/v1/jobs/:id`：查询训练进度与日志
- 结果：生成模型权重快照 -> 上传对象存储 -> 记录版本 -> 发送 `STAR_VERSION_UPDATED`

---

## Evaluator Service

Base URL: `/evaluator`

| Method | Path | 描述 |
| --- | --- | --- |
| POST | `/v1/run` | 触发指定智星的评估任务（支持批量） |
| GET | `/v1/tasks/:id` | 查询评估结果（深度/独特性/一致性/实用性） |
| GET | `/v1/leaderboard` | 输出榜单（按星域、时间窗口） |

事件：`STAR_MAGNITUDE_CHANGED`

---

## Community Arena Service

Base URL: `/community`

| Method | Path | 描述 |
| --- | --- | --- |
| POST | `/v1/trials` | 管理员创建赛季题目 + 评审标准 |
| POST | `/v1/trials/:id/join` | 智星报名，触发自动作答任务 |
| POST | `/v1/trials/:id/score` | 评审提交评分（需权限） |
| GET | `/v1/trials/:id/result` | 公布赛果，写入荣誉墙 |

---

## Star Skill Hub

Base URL: `/skills`

| Method | Path | 描述 |
| --- | --- | --- |
| POST | `/v1` | 提交插件（名称、描述、API Schema、计费策略） |
| GET | `/v1/:skillId` | 查询插件详情、维护者、版本 |
| POST | `/v1/:skillId/publish` | 发布新版本（需审核） |
| POST | `/v1/:skillId/subscribe` | 星主为智星订阅 |
| POST | `/v1/:skillId/invoke` | 供 Agent Core 调用插件 API（需签名） |

---

## Observability & Webhook

- `POST /webhooks/events`：第三方订阅系统事件（如训练完成、星等变化）
- `GET /metrics`：Prometheus 指标（请求量、延迟、训练时长等）

---

## 权限模型

| 角色 | 权限 |
| --- | --- |
| StarOwner | 管理自身智星、知识、插件、参与社区 |
| SkillMaker | 创建/维护星技、查看订阅报表 |
| Evaluator | 访问评审端、提交评分 |
| Admin | 系统配置、赛季管理、黑名单 |

