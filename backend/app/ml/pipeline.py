"""Cached genuine learned inference and independently explainable urgency."""

from functools import lru_cache
import hashlib
import re
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import DBSCAN
from app.core.config import ROOT, ARTIFACTS, settings

MODEL = ARTIFACTS / "classifiers.joblib"


def train():
    path = ROOT / "data/sample_complaints.csv"
    df = pd.read_csv(path)
    models = {}
    for label in ["category", "sentiment"]:
        pipe = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2), sublinear_tf=True, max_features=18000
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        class_weight="balanced", max_iter=1000, random_state=42
                    ),
                ),
            ]
        )
        pipe.fit(df.complaint_text, df[label])
        models[label] = pipe
    models["version"] = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    joblib.dump(models, MODEL)
    load_models.cache_clear()
    return models


@lru_cache(maxsize=1)
def load_models():
    if not MODEL.exists():
        raise FileNotFoundError("Models missing. Run python scripts/train.py first.")
    return joblib.load(MODEL)


def urgency(text):
    t = text.lower()
    if re.search(
        r"unauthori[sz]ed|compromis|stolen|identity theft|suspected fraud|phishing|impersonat|suspicious debit|stranger",
        t,
    ):
        return (
            "Critical",
            "security_risk: possible unauthorized activity; human review required",
        )
    if (
        re.search(r"fail|unsuccess|nothing|not.*reach", t)
        and re.search(r"deduct|debit|reduced|money|balance", t)
    ) or re.search(r"charged twice|duplicate charge|two identical", t):
        return "High", "funds_at_risk: failed debit or repeated charge"
    if re.search(
        r"cannot|unable|locked|crash|not replied|four days|waiting|unresolved|shut out",
        t,
    ):
        return "Medium", "service_disruption: access, stability or unresolved service"
    return "Low", "routine_feedback: no elevated risk rule matched"


def predict(texts):
    m = load_models()
    result = []
    cp = m["category"].predict_proba(texts)
    sp = m["sentiment"].predict_proba(texts)
    for i, t in enumerate(texts):
        u, r = urgency(t)
        result.append(
            dict(
                category=str(m["category"].classes_[cp[i].argmax()]),
                confidence=float(cp[i].max()),
                sentiment=str(m["sentiment"].classes_[sp[i].argmax()]),
                sentiment_confidence=float(sp[i].max()),
                urgency=u,
                urgency_reason=r,
                model_version=m["version"],
            )
        )
    return result


@lru_cache(maxsize=1)
def sentence_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model, device="cpu")


def embed(texts):
    if settings.embedding_mode == "tfidf":
        return TfidfVectorizer(
            ngram_range=(1, 2), max_features=8000, sublinear_tf=True
        ).fit_transform(texts), "tfidf-lexical"
    if settings.embedding_mode != "sentence-transformer":
        raise ValueError("Unknown embedding_mode")
    cache = ARTIFACTS / "embeddings"
    cache.mkdir(exist_ok=True)
    keys = [
        hashlib.sha256((settings.embedding_model + "\0" + t).encode()).hexdigest()
        for t in texts
    ]
    missing = {k: t for k, t in zip(keys, texts) if not (cache / f"{k}.npy").exists()}
    if missing:
        vectors = sentence_model().encode(
            list(missing.values()),
            batch_size=64,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        for key, vector in zip(missing, vectors):
            np.save(cache / f"{key}.npy", vector)
    return np.stack(
        [np.load(cache / f"{k}.npy", allow_pickle=False) for k in keys]
    ), settings.embedding_model


def group(texts):
    if len(texts) < 3:
        return [-1] * len(texts), settings.embedding_mode
    # Strip synthetic reference IDs before clustering to avoid identifier-driven similarity.
    cleaned = [
        re.sub(r" This concerns my .*?reference SYN-\d+\.", "", t) for t in texts
    ]
    vectors, method = embed(cleaned)
    labels = DBSCAN(eps=0.28, min_samples=3, metric="cosine", n_jobs=2).fit_predict(
        vectors
    )
    return labels.tolist(), method
