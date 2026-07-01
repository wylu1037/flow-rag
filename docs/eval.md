# FlowRAG Evaluation

The MVP includes service-level tests for two core cases:

1. A grounded question retrieves evidence and returns citations.
2. An unsupported question does not fabricate an answer.

Run:

```bash
cd apps/api
uv --cache-dir .uv-cache run --no-sync python -m unittest discover -s tests
```

The root workspace also exposes the same check:

```bash
pnpm test:api
```

Future eval work should add a dataset with expected answers and expected sources, then compute:

| Metric | Purpose |
|---|---|
| Retrieval Recall@K | Whether the expected chunk appears in retrieved candidates |
| Citation Precision | Whether returned citations support the answer |
| Faithfulness | Whether answer claims are grounded in evidence |
| Unsupported Claim Count | Whether verifier catches missing evidence |
| Latency | Whether agentic steps stay within budget |
