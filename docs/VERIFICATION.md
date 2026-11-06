# Executed verification

Executed 6 November 2026 on Linux, Python 3.12.14, Node.js 24.22.1, npm 11.9.0. Windows instructions are documented, not executed on Windows.

## Results

| Check | Actual result |
| --- | --- |
| `python -m pytest backend/tests -c backend/pytest.ini -q` | 24 passed, one dependency deprecation warning |
| `npm --prefix frontend test` | 7 passed |
| `npm --prefix frontend run build` | TypeScript and Vite production build passed; chart/vendor chunks separated |
| `CHROMIUM_PATH=/usr/bin/chromium npm run test:e2e` from frontend | 1 complete real-browser workflow passed |
| `python scripts/generate_data.py` | 2,400 training/demo rows and 112 held-out rows generated |
| `python scripts/train.py` | Both classifiers trained and saved; model version `331702d01328ef90` |
| `python scripts/seed.py`, repeated | First import 2,400; repeat imported 0, duplicate count 2,400; uploaded browser record retained |
| `python scripts/evaluate.py` | Actual metrics persisted to artifacts/evaluation.json and data/evaluation/results.json |
| `python -m pip check` | No broken requirements |
| `ruff check backend scripts` | Passed |
| `bash scripts/cloud-install.sh` | Repeat install succeeded without replacing prepared database |
| Documented uvicorn + Vite commands | Started, stopped and restarted; HTTP health and proxied analytics verified |

Backend coverage includes CSV schema/row errors, malformed/oversized/wrong-type uploads, duplicate detection, trained category and sentiment inference, urgency reasons, DB persistence, pagination/filter validation, clustering/noise, aggregate counts, insights and evidence IDs, mocked OpenAI/Gemini contracts, timeout fallback, embedding cache reuse with a mocked encoder, failed-job retry, concurrency conflict and missing-model 503.

Frontend tests cover dashboard metrics, API errors, navigation, server filter/search parameters, multipart upload results, evidence and priorities, and filter reset. Chromium verification navigates all seven pages, filters actual persisted data, opens complaint and cluster dialogs, generates real deterministic insights, imports valid/invalid CSV, polls analysis to completion and checks Settings. Screenshot in docs/dashboard.png is from the real loaded dashboard. One browser-test complaint is intentionally retained; total after verification is 2,401.

## ML measurements

112 independently phrased **synthetic** examples; 2,400 training examples. No exact-text intersection. Train/evaluation complaint base phrases and sentiment clauses are separately authored. Shared domain vocabulary and a narrow synthetic grammar remain limitations.

| Metric | Category | Sentiment |
| --- | --- | --- |
| Accuracy | 0.6339 | 0.6161 |
| Macro precision | 0.6903 | 0.6292 |
| Macro recall | 0.6339 | 0.5903 |
| Macro F1 | 0.6406 | 0.6056 |

Lexical clustering diagnostic on 300 fixed-seed samples: 39 groups, 146 noise records, cosine silhouette 0.5852 on non-noise records. This is not a semantic-retrieval quality score. Per-class reports, confusion matrices and actual grouped examples are in the machine-readable results. These modest synthetic scores are reported honestly; real-world banking accuracy remains unproven.

## External limits and unverified behavior

- Sentence-transformers and CPU PyTorch were installed successfully. The real MiniLM model request was rejected by the network proxy (403 for huggingface.co), so actual semantic inference is **blocked and unverified**. TF-IDF fallback is functional and explicitly labeled. Encoder/cache contract tests use a mock; they do not establish MiniLM quality.
- OpenAI and Gemini adapters were exercised with mocked HTTP responses and exceptions, including unknown evidence rejection. No live key/model was configured or requested. Live access, rate limits, model compatibility and output quality remain unverified.
- Initial sandboxed networking and TestClient event-loop calls were blocked; authorized commands outside the command sandbox used the existing proxy, authentication and TLS trust. No policy bypass or TLS verification disabling was used.
- The first browser run exposed an accessible-link-name mismatch caused by a decorative badge. It was fixed and subsequent full runs passed. An additional browser launch inside the command sandbox failed due to blocked Chromium sockets; browser verification used the supported execution approval route.
- One upstream TestClient/AnyIO deprecation warning is non-fatal.

## Saved cloud configuration

Draft saves were confirmed for `install_script`, `start_skill`, and four explicit model-host domains: huggingface.co, cas-bridge.xethub.hf.co, cas-server.xethub.hf.co, transfer.xethub.hf.co. Existing package-manager presets were preserved. No secret values were saved or exposed. The running policy still has no custom hosts, so the model-host change is not applied yet. Review/save the draft in environment settings, then publish the prepared environment. Publication and restoration into a fresh task were not performed or verified.

No remote push, Git commit, deployment, or production readiness claim was made. All project files are present in the original checkout; generated dependencies, database and model artifacts remain ignored.
