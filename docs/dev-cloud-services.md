# 免费托管开发环境

这份文档记录 FlowRAG 开发环境可直接使用的免费云产品，以及如何申请和配置到 `.env`。目标是：本地只运行 `FastAPI`、`worker`、`Next.js`，数据库、Redis、对象存储使用免费托管服务。

免费额度和产品入口可能调整，正式使用前以各产品控制台显示为准。不要把真实密钥提交到 Git。

## 推荐组合

### 最省心组合

```text
Supabase Free
- PostgreSQL
- pgvector
- Storage 可选

Upstash Redis Free
- Redis URL
- 限流、缓存、任务状态
```

适合快速开发和 demo。Supabase 同时提供 Postgres、pgvector 和对象存储，Upstash 补 Redis。

### 更贴近生产的组合

```text
Supabase Free 或 Neon Free
- PostgreSQL + pgvector

Upstash Redis Free
- Redis

Cloudflare R2 Free Tier
- S3-compatible object storage
```

适合后续按 S3 协议接对象存储，和生产架构更接近。

## 环境变量总览

复制 `.env.example` 为 `.env`，再把下面变量替换为云产品控制台里的值。

```env
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=rediss://...

OBJECT_STORAGE_ENDPOINT=https://...
OBJECT_STORAGE_BUCKET=flowrag
OBJECT_STORAGE_ACCESS_KEY=...
OBJECT_STORAGE_SECRET_KEY=...

LLM_BASE_URL=...
LLM_API_KEY=...
LLM_MODEL=...
EMBEDDING_MODEL=...
RERANKER_MODEL=...
```

当前本地 MVP 的 repository、embedding、LLM 和对象存储仍有内存/本地实现，部分云 env 是为接入持久层和真实 provider 预留的。接入 PostgreSQL、Redis worker 和对象存储后，应优先复用这些变量名。

## Supabase Free

用途：

- PostgreSQL
- pgvector
- 可选对象存储

申请步骤：

1. 打开 `https://supabase.com` 并注册账号。
2. 创建一个新 project。
3. 选择 Free plan、区域和数据库密码。
4. 进入 `Project Settings -> Database -> Connection string`。
5. 复制 URI 连接串，并替换密码占位符。

启用 pgvector：

1. 进入 `SQL Editor`。
2. 执行：

```sql
create extension if not exists vector;
```

配置 `.env`：

```env
DATABASE_URL=postgresql+psycopg://postgres:<password>@<host>:5432/postgres?sslmode=require
```

注意：

- Supabase 可能提供 direct connection、transaction pooler、session pooler 等连接串。开发环境优先用 direct connection；serverless 或连接数紧张时再用 pooler。
- 如果后续使用迁移工具，迁移通常更适合 direct connection。
- 如果要使用 Supabase Storage 的 S3-compatible API，进入 `Storage -> Settings -> S3 access keys` 创建 access key。endpoint 通常形如：

```env
OBJECT_STORAGE_ENDPOINT=https://<project-ref>.supabase.co/storage/v1/s3
OBJECT_STORAGE_BUCKET=flowrag
OBJECT_STORAGE_ACCESS_KEY=<supabase-s3-access-key>
OBJECT_STORAGE_SECRET_KEY=<supabase-s3-secret-key>
```

## Neon Free

用途：

- PostgreSQL
- pgvector

申请步骤：

1. 打开 `https://neon.tech` 并注册账号。
2. 创建一个 project。
3. 进入 project dashboard，复制 connection string。
4. 在 SQL editor 里启用 pgvector。

启用 pgvector：

```sql
create extension if not exists vector;
```

配置 `.env`：

```env
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>/<database>?sslmode=require
```

注意：

- Neon 是 serverless Postgres，免费层可能冷启动。
- Neon 只解决数据库，不提供 Redis 和对象存储。

## Upstash Redis Free

用途：

- Redis
- rate limit
- cache
- job state
- queue metadata

申请步骤：

1. 打开 `https://upstash.com` 并注册账号。
2. 进入 `Redis`，创建 database。
3. 选择 Free plan 和离开发环境较近的 region。
4. 创建后进入 database detail。
5. 复制 `Redis URL` 或 `TLS URL`。

配置 `.env`：

```env
REDIS_URL=rediss://default:<password>@<host>:<port>
```

注意：

- 如果控制台提供 `redis://` 和 `rediss://`，云环境优先用 `rediss://`。
- Upstash 也提供 REST URL/token，但当前项目建议先统一使用 `REDIS_URL`，方便以后替换 Python Redis client。
- 当前代码里的限流器是本地内存实现，接 Redis 后可替换为 Redis-backed limiter。

## Cloudflare R2 Free Tier

用途：

- S3-compatible object storage
- 原始上传文件
- 解析产物
- 后续 chunk 中间产物

申请步骤：

1. 打开 `https://dash.cloudflare.com` 并注册账号。
2. 进入 `R2 Object Storage`。
3. 创建 bucket，例如 `flowrag`。
4. 进入 `R2 -> Manage R2 API tokens`。
5. 创建 API token，权限选择对象读写，作用域限制到该 bucket。
6. 记录 `Access Key ID`、`Secret Access Key` 和账号级 S3 endpoint。

配置 `.env`：

```env
OBJECT_STORAGE_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
OBJECT_STORAGE_BUCKET=flowrag
OBJECT_STORAGE_ACCESS_KEY=<r2-access-key-id>
OBJECT_STORAGE_SECRET_KEY=<r2-secret-access-key>
```

注意：

- R2 不收取 egress 费用，但免费额度仍有限制。
- 如果后端使用 S3 SDK，通常还需要关闭 path-style/region 相关差异，具体以 SDK adapter 实现为准。

## 可选：托管 LLM / Embedding

本地 MVP 默认可不配置真实 LLM key。需要开发真实回答质量时，可以选择带免费额度或试用额度的 OpenAI-compatible provider。

可选产品：

- Google AI Studio / Gemini
- Groq
- OpenRouter
- Jina AI embeddings
- Cohere trial

配置示例：

```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=<provider-api-key>
LLM_MODEL=<model-name>
EMBEDDING_MODEL=<embedding-model-name>
RERANKER_MODEL=<reranker-model-name>
```

注意：

- 不同 provider 的免费额度、速率限制和模型名称变化很快。
- 如果 provider 不兼容 OpenAI API，需要在后端增加对应 adapter。

## 可选：可观测性

开发环境可以先只用本地日志。要接云端免费可观测性时：

| 能力 | 免费云产品 | env 建议 |
|---|---|---|
| Error tracking | Sentry Free | `SENTRY_DSN=...` |
| Metrics / logs / traces | Grafana Cloud Free | `OTEL_EXPORTER_OTLP_ENDPOINT=...`、`OTEL_EXPORTER_OTLP_HEADERS=...` |

当前项目还没有正式接入 Sentry/OpenTelemetry exporter。接入时建议保留这些变量名。

## 可选：Backend hosting

本地开发不需要 Backend hosting；你可以直接运行：

```bash
cd apps/api
uv --cache-dir .uv-cache run uvicorn app.main:app --reload --port 8000
```

只有需要让别人访问、接 webhook、跑线上 demo 或长期 worker 时，才需要托管后端。

可选免费/低价产品：

- Render
- Railway
- Fly.io
- Google Cloud Run

配置时把同一套 `.env` 填到对应平台的 environment variables 里即可。

## 推荐落地顺序

1. 创建 Supabase 或 Neon，配置 `DATABASE_URL`。
2. 执行 `create extension if not exists vector;`。
3. 创建 Upstash Redis，配置 `REDIS_URL`。
4. 如果使用对象存储，创建 Cloudflare R2 bucket 并配置 `OBJECT_STORAGE_*`。
5. 本地保留 `.env`，不要提交。
6. 启动本地后端和前端。

```bash
cd apps/api
uv --cache-dir .uv-cache run uvicorn app.main:app --reload --port 8000
```

```bash
cd apps/web
pnpm dev --hostname 127.0.0.1 --port 3000
```

## 常见问题

### 免费数据库第一次请求很慢

Supabase/Neon 免费层可能有冷启动或休眠。开发环境可以接受；线上 demo 需要提前预热。

### 连接串里应该用 `postgresql://` 还是 `postgresql+psycopg://`

Python SQLAlchemy + psycopg 建议使用：

```env
DATABASE_URL=postgresql+psycopg://...
```

如果某个云控制台只给 `postgresql://...`，可以手动改成 `postgresql+psycopg://...`。

### Redis URL 应该用 `redis://` 还是 `rediss://`

托管云 Redis 优先用 TLS：

```env
REDIS_URL=rediss://...
```

### 可以只用 Supabase 吗

可以。Supabase 可以覆盖 PostgreSQL、pgvector、对象存储。Redis 能力仍建议用 Upstash 补齐。
