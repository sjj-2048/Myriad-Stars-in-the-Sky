# 数据库与存储设计

> 采用 PostgreSQL（事务数据）+ MongoDB（非结构化对话/日志）+ MinIO（对象）+ 向量库（Milvus/PgVector）。

## 1. PostgreSQL 表结构

### 1.1 `users`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | UUID PK | 用户 ID |
| `email` | citext unique | 登录邮箱 |
| `password_hash` | text | Bcrypt/Argon2 |
| `display_name` | varchar(80) | 昵称 |
| `avatar_url` | text | 头像 |
| `role` | enum(`star_owner`,`skill_maker`,`admin`) | 角色 |
| `preferences` | jsonb | 通知/隐私设置 |
| `created_at` | timestamptz | 创建时间 |

### 1.2 `stars`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | UUID PK |
| `owner_id` | UUID FK -> users |
| `name` | varchar(80) |
| `domain` | varchar(120) | 星域（例如“古籍修复”）|
| `persona` | text | 人格设定 |
| `tone` | varchar(40) | 交流风格 |
| `status` | enum(`active`,`paused`,`archived`) |
| `current_model_version` | UUID FK -> star_model_versions |
| `tags` | text[] |
| `created_at` | timestamptz |
| `updated_at` | timestamptz |

### 1.3 `star_model_versions`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | UUID PK |
| `star_id` | UUID FK |
| `version_name` | varchar(40) |
| `artifact_uri` | text | MinIO/对象存储链接 |
| `training_method` | enum(`qlora`,`dpo`,`sft`) |
| `training_data_span` | tstzrange | 数据窗口 |
| `metrics` | jsonb |
| `created_at` | timestamptz |

### 1.4 `knowledge_tasks`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | UUID |
| `star_id` | UUID |
| `source_type` | enum(`upload`,`webhook`,`note`) |
| `status` | enum(`pending`,`processing`,`completed`,`failed`) |
| `payload_uri` | text | 原文对象地址 |
| `chunk_count` | int |
| `embedding_index` | text | 向量库集合名 |
| `error` | text |
| `created_at` | timestamptz |
| `completed_at` | timestamptz |

### 1.5 `conversations`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `star_id` | UUID |
| `user_id` | UUID |
| `channel` | enum(`web`,`mobile`,`api`,`trial`) |
| `status` | enum(`active`,`closed`) |
| `feedback_score` | smallint |
| `created_at` | timestamptz |
| `closed_at` | timestamptz |

### 1.6 `conversation_feedback`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `conversation_id` | UUID |
| `rating` | smallint (1-5) |
| `comment` | text |
| `labels` | text[] (深度/准确等标签) |
| `created_at` | timestamptz |

### 1.7 `magnitude_history`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `star_id` | UUID |
| `depth` | numeric(5,2) |
| `originality` | numeric(5,2) |
| `consistency` | numeric(5,2) |
| `utility` | numeric(5,2) |
| `overall` | numeric(5,2) |
| `level` | enum(`L1`,`L2`,`L3`,`L4`,`L5`) |
| `evaluated_at` | timestamptz |

### 1.8 `star_trials`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `season_id` | uuid |
| `title` | varchar(120) |
| `prompt` | text |
| `answer_schema` | jsonb |
| `status` | enum(`draft`,`ongoing`,`finished`) |
| `created_by` | UUID |
| `created_at` | timestamptz |

### 1.9 `trial_entries`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `trial_id` | UUID |
| `star_id` | UUID |
| `response_uri` | text |
| `score` | numeric(5,2) |
| `rank` | int |
| `reward_points` | int |
| `submitted_at` | timestamptz |

### 1.10 `skills`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `owner_id` | UUID |
| `name` | varchar(80) |
| `description` | text |
| `api_endpoint` | text |
| `schema` | jsonb |
| `pricing_type` | enum(`free`,`subscription`,`usage`) |
| `price` | numeric |
| `status` | enum(`draft`,`pending_review`,`published`,`suspended`) |
| `created_at` | timestamptz |

### 1.11 `skill_subscriptions`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `skill_id` | UUID |
| `star_id` | UUID |
| `plan` | varchar(40) |
| `status` | enum(`active`,`expired`,`cancelled`) |
| `current_period_end` | timestamptz |

### 1.12 `webhooks`
| 字段 | 类型 |
| --- | --- |
| `id` | UUID |
| `owner_id` | UUID |
| `url` | text |
| `event_types` | text[] |
| `secret` | text |
| `status` | enum |
| `created_at` | timestamptz |

---

## 2. MongoDB 集合

1. `conversation_messages`
   - `conversationId`
   - `sender` (`user`/`star`)
   - `content`
   - `tokens`
   - `toolCalls`
   - `createdAt`

2. `knowledge_chunks`
   - `taskId`
   - `starId`
   - `chunkText`
   - `embeddingVectorId`
   - `metadata`

3. `training_logs`
   - `jobId`
   - `starId`
   - `phase` (`prepare`,`train`,`evaluate`)
   - `stdout`
   - `metrics`

---

## 3. 向量库（Milvus/PgVector）

- 集合命名：`star_<starId>`
- 字段：`id`, `star_id`, `chunk_id`, `embedding[1536]`, `metadata`（来源、时间、标签）
- 索引：HNSW / IVF_FLAT

---

## 4. 对象存储（MinIO/S3 兼容）

| Bucket | 内容 |
| --- | --- |
| `knowledge-raw` | 原始上传文件 |
| `model-artifacts` | 训练产出（LoRA 权重、全量权重） |
| `trial-responses` | 星试回答 JSON/音频/视频 |
| `exports` | 星等报告、白皮书等 |

---

## 5. 审计与合规

- 日志：应用日志进入 Loki/Elastic；训练日志同时写对象存储。
- 数据隔离：`row level security` 确保星主仅访问自己的智星。
- 备份策略：PostgreSQL + MongoDB 每日快照，MinIO 版本化。

