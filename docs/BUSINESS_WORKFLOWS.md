# Workflows and rules
1. Import UTF-8 CSV (≤5 MB, ≤10,000 rows). Required columns: complaint_id, complaint_text, created_at. Optional customer_id, source, category. Dates must be ISO dates/times, normalized to UTC. Invalid rows return row numbers and reasons; duplicate IDs are counted separately. All accepted rows commit atomically with the import batch.
2. Analyze pending complaints. One background analysis job at a time; category and sentiment use cached trained models, urgency uses independent reason codes. Persist results and cluster all processed records. Restart marks interrupted jobs failed; retry processes remaining records and rebuilds clusters.
3. Overview filters category, sentiment, urgency, source and inclusive UTC dates. The backend computes every business metric.
4. Search, sort and paginate complaints; inspect confidence, method, reasons and supporting issue members.
5. Generate insights from recurring issues. Priority = 100 × (0.45 relative frequency + 0.35 mean severity/4 + 0.20 recency), recency = exp(-age_days/30). Age is relative to latest stored complaint for reproducible demo snapshots. Evidence and numeric values come from SQL/Python. Provider output is bounded, validated and labeled; errors return an explicit deterministic fallback.

Edge cases: empty/malformed/oversized CSV, duplicate rows in one file or previous batches, empty filters, unclustered noise, unconfigured or failing AI, interrupted processing, no evaluated model. Never overwrite imported data on startup.
