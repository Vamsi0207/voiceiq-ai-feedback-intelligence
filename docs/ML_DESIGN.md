# ML and evaluation
A fixed-seed generator writes 2,400 imbalanced synthetic training/demo examples. Category-specific training sentences combine sentiment clauses, source/date variation and informal wording. Evaluation uses independently authored phrasings, not substitutions in training templates. Evaluation phrases are excluded from training. This remains a small synthetic benchmark: repeated generation grammar and vocabulary make scores optimistic; real-world generalization is unproven.

TF-IDF (word unigrams/bigrams, sublinear TF) + balanced logistic regression predicts eight categories and three sentiments. Confidence is maximum model probability, not calibrated risk. Version is a SHA-256 digest of training data. joblib artifacts load only from locally generated trusted files.

Urgency uses reason-coded security, lost funds, repeated charges, access and delay rules; sentiment alone cannot trigger critical. It is a triage aid, not a fraud verdict.

SentenceTransformer all-MiniLM-L6-v2 embeddings are normalized and cached on disk per text hash/model. DBSCAN cosine eps=0.28, min_samples=3 groups recurring issues; noise remains unclustered. Optional tfidf mode uses lexical cosine, explicitly reported. No reclustering on dashboard requests.

Run scripts/evaluate.py for accuracy, macro precision/recall/F1, per-class F1, confusion matrix, sentiment metrics and clustering diagnostics/examples. Inspect low-performing classes; no production performance target is asserted. Negation, mixed sentiment, novel complaint topics, code switching and spelling variation are expected failure modes.
