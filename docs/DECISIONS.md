# Decisions
- SQLite and create_all for this fresh local MVP; schema changes require explicit migration before production. No destructive auto reset.
- Train both classifiers locally: reproducible and no paid inference dependency. Synthetic metrics measure a narrow benchmark, not real banking quality.
- DBSCAN cosine with min_samples=3 admits noise. Sentence-transformers all-MiniLM-L6-v2 (CPU) is preferred. Explicit embedding mode=tfidf provides a documented lexical fallback if downloads are unavailable; never label it semantic embeddings.
- Analysis is a single-process background job. No Redis/Celery; one server worker only. Cluster IDs may change on analysis, and existing insights are invalidated atomically.
- External AI is opt-in via provider, key and model. No guessed model identifiers. Deterministic summaries quote stored evidence, and recommendations are suggestions with hypotheses, not diagnosed root causes.
- No automatic seeding or credential storage in UI. Seed is explicit and idempotent. Data and artifacts are excluded from version control.
