# VoiceIQ requirements
Product and support managers need traceable patterns in banking feedback. Analysts need searchable evidence and honest model evaluation.

The MVP imports CSV, validates each row, deduplicates IDs, trains classifiers, processes complaints in background batches, clusters issues, and exposes calculated analytics and grounded recommendations. Seven pages cover overview, explorer, clusters, insights, evaluation, import and settings.

Acceptance: import → analyze → inspect persisted classification and urgency → filter aggregate metrics → inspect recurring evidence → prioritize. Every insight references stored complaints. No API key is needed. No authentication: bind locally; production deployment is outside scope.

Constraints: CPU inference, a few thousand English synthetic records, SQLite single writer, bounded uploads and prompts. No real PII, automated fraud decisions, regulatory claims, or automatic recommendation execution.
