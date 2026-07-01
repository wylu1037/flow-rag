# FlowRAG Skills Plan

This project should use project-scoped skills for work that will repeat across the FlowRAG buildout: RAG architecture, Next.js frontend work, FastAPI backend work, evaluation, testing, documentation, and deployment.

## Current Status

`npx skills` could not be executed from the agent environment because the network escalation was rejected by the tool authorization layer before the command started.

Attempted command:

```bash
npx --yes skills --help
```

Observed blocker:

```text
Automatic approval review failed before npx could run.
```

## Search Queries

Run these from the project root:

```bash
npx --yes skills find rag
npx --yes skills find agentic rag
npx --yes skills find retrieval
npx --yes skills find evaluation
npx --yes skills find nextjs --owner vercel-labs
npx --yes skills find react --owner vercel-labs
npx --yes skills find fastapi
npx --yes skills find testing
npx --yes skills find playwright
npx --yes skills find docker
npx --yes skills find architecture
npx --yes skills find api-docs
```

## Selection Criteria

Prefer skills that meet most of these conditions:

1. Install count is at least 1,000.
2. Source is reputable, such as `vercel-labs`, `anthropics`, `microsoft`, or another well-known maintainer.
3. The source repository has at least 100 GitHub stars.
4. The skill maps directly to planned FlowRAG work.
5. The skill adds concrete implementation or review guidance, not only generic advice.

Avoid project installation for skills with very low install counts, unclear ownership, or broad permissions unless they are reviewed first.

## Recommended Skill Areas

| Area | Why FlowRAG needs it |
|---|---|
| RAG / retrieval | Query rewrite, hybrid retrieval, reranking, citation quality, and faithfulness checks |
| Agent workflows | Planning, tool calling, loop control, traceability, and failure recovery |
| Next.js / React | Chat UI, document management, trace panel, streaming UX |
| FastAPI / Python | API design, SSE, background jobs, service layering |
| Evaluation / testing | RAG regression sets, faithfulness, citation precision, retrieval recall |
| Playwright / E2E | Upload, ingestion status, chat streaming, citation inspection |
| Docker / deployment | Postgres, Redis, API, worker, web, and object storage composition |
| Documentation | Architecture docs, API docs, eval docs, implementation roadmap |

## Project-Scoped Installation

Install selected skills from the project root without the global `-g` flag:

```bash
npx --yes skills add <owner/repo@skill> -y
```

Then verify what changed:

```bash
find . -maxdepth 4 -type f
npx --yes skills check
```

If the CLI asks whether to install globally or locally, choose the local/project option.
