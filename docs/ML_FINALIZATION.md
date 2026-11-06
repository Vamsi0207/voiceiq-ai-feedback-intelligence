# ML finalization: frozen data and release decisions

## What the baseline revealed

The original training CSV contains 2,400 synthetic records but only eight categories, 48 base complaint templates and nine main affect clauses. Synthetic reference IDs made texts unique without adding linguistic coverage. The evaluation CSV contains 112 records derived from 32 independently authored complaint bases, paired with separate affect clauses. Both datasets are much less diverse than their row counts suggest.

Baseline category macro-F1 was 0.6406. The weakest per-class F1 values were Fraud & Security (0.3846), Customer Support (0.4000) and Account Access (0.4390). Nine of fourteen fraud records were predicted as account access: shared banking/access words outweighed unseen security vocabulary. Support paraphrases also mapped to several other categories. Character features can help morphology and spelling but cannot supply missing semantic knowledge.

Baseline sentiment macro-F1 was 0.6056, with 17 neutral records predicted negative and 14 negative records predicted neutral; only eight of sixteen positive records were correctly predicted. Nine repetitive training affect clauses provide poor coverage of unfamiliar language. Some neutral-labeled records describe negative incidents followed by neutral requests: labels reflect the appended affect clause rather than a universally defensible full-document interpretation. This ambiguity was retained and documented, not silently relabeled.

## Candidate and selection procedure

One fixed candidate was implemented before final held-out evaluation:

- Normalize Unicode and spacing; remove the synthetic reference suffix.
- Combine word unigrams/bigrams and character-within-word 3–5 grams with Logistic Regression.
- For sentiment, also feed eight VADER valence features: full-text and final-sentence negative/neutral/positive/compound scores. VADER 3.3.2 supplies an independent published English lexicon; no held-out examples or labels are used to build it. Logistic Regression learns how to combine these features from the original training set.

`scripts/validate_models.py` reads **only training data**, using three fixed grouped folds. Category grouping keeps copies of a base complaint together; sentiment grouping keeps copies of an affect clause together. Models and vectorizers fit only each fold's training partition. No held-out text, labels, error examples or synonyms were added to training. Training examples were not generated to imitate evaluation phrases.

| Training grouped validation macro-F1 | Baseline | Candidate |
| --- | --- | --- |
| Category | 0.5662 | 0.6335 |
| Sentiment | 0.4551 | 0.9287 |

`training_validation.json` preserves fold-level results. This is still synthetic grouped validation and is not representative of an independent real-world corpus.

## Frozen-set results and conservative release gate

The candidate was then evaluated on the same unchanged 112 records. Category macro-F1 fell to **0.6280**, despite improved training validation. That category change was rejected; the existing category baseline is retained. Sentiment macro-F1 improved to **0.9218** and was retained. No subsequent hyperparameter search or phrase additions were performed against the held-out errors. `candidate_results.json` preserves the rejected category trial as well as its confusion matrix.

| Metric | Category before | Category released | Sentiment before | Sentiment released |
| --- | --- | --- | --- | --- |
| Accuracy | 0.6339 | 0.6339 | 0.6161 | 0.9554 |
| Macro precision | 0.6903 | 0.6903 | 0.6292 | 0.9686 |
| Macro recall | 0.6339 | 0.6339 | 0.5903 | 0.8958 |
| Macro F1 | 0.6406 | 0.6406 | 0.6056 | 0.9218 |

Released sentiment per-class F1: Negative 1.0000, Neutral 0.9505, Positive 0.8148. Five of sixteen positive examples are still predicted neutral. The large gain benefits from the synthetic convention of putting an affect sentence last; mixed real feedback, sarcasm, banking jargon and code switching remain unproven.

The held-out set was inspected for diagnosis and used as a **release regression gate**, so these scores are retrospective comparisons, not an untouched future test. No held-out rows entered fitting or cross-validation, but release selection can still bias reported comparisons. A newly collected, blinded representative evaluation set is required before any generalization claim. No real-world accuracy or business impact claim is made.

## Reproducibility and artifacts

- Frozen held-out SHA256: `c8680baf9ce0d1a384b0d8e0bf84d97f795cb3ce0c08c82a5e881fa0a9de09bc`.
- Training CSV remains byte-for-byte identical to the initial source commit. Its SHA256 prefix is `331702d01328ef90`.
- Released model: `a100fa23057222b9`. Version signature now includes training data, feature source, feature version and the selected feature sets; models no longer share a version merely because their training CSV matches.
- `baseline.json`: original executed evaluation; `candidate_results.json`: full candidate evaluation; `results.json`: released model; `comparison.json`: actual deltas and misclassified records.
- Training, candidate evaluation, seed and frozen-set comparison scripts were executed. Grouped validation is reproducible with `python scripts/validate_models.py`; it reports the candidate trial, not the conservative release decision. Train the release with `python scripts/train.py`, then evaluate and compare with `scripts/evaluate.py` and `scripts/compare_evaluation.py`.
- After training, restart the backend and run analysis. Completed complaints with an older model version are reprocessed. Uploaded records are preserved. The upgrade path has an integration test.

## Semantic grouping remains separate

MiniLM and its CPU dependencies are installed, but huggingface.co still returned proxy CONNECT 403 on finalization. Lexical DBSCAN remains explicitly enabled. A real-model opt-in test checks local MiniLM embeddings, relative semantic similarity, clustering/noise and cache reuse; it is skipped in the ordinary suite and has not executed successfully against the actual model. Applying the saved network settings and downloading the model are external prerequisites. No semantic-quality improvement is claimed from the classifier work.
