"""Training-only feature design; no evaluation text or labels are accessed here."""

from functools import lru_cache
import re
import unicodedata
import numpy as np
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

FEATURE_VERSION = "word-char-vader-v2"


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"\s*this concerns my .*?reference syn-\d+\.?", "", text)
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=1)
def sentiment_analyzer():
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    return SentimentIntensityAnalyzer()


def sentiment_features(texts):
    analyzer = sentiment_analyzer()
    rows = []
    for text in texts:
        # Preserve casing/punctuation for VADER's independent language heuristics.
        clean = re.sub(r"\s*This concerns my .*?reference SYN-\d+\.?", "", text)
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean) if s.strip()]
        scores = [
            analyzer.polarity_scores(clean),
            analyzer.polarity_scores(sentences[-1] if sentences else clean),
        ]
        rows.append(
            [
                score[key]
                for score in scores
                for key in ("neg", "neu", "pos", "compound")
            ]
        )
    return np.asarray(rows)


def build_classifier(task: str, improved=True):
    if not improved:
        features = TfidfVectorizer(
            ngram_range=(1, 2), sublinear_tf=True, max_features=18000
        )
    else:
        branches = [
            (
                "word",
                TfidfVectorizer(
                    preprocessor=normalize_text,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    max_features=18000,
                ),
            ),
            (
                "character",
                TfidfVectorizer(
                    preprocessor=normalize_text,
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    sublinear_tf=True,
                    max_features=24000,
                ),
            ),
        ]
        if task == "sentiment":
            branches.append(
                ("valence", FunctionTransformer(sentiment_features, validate=False))
            )
        features = FeatureUnion(branches)
    return Pipeline(
        [
            ("features", features),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced", max_iter=1000, random_state=42
                ),
            ),
        ]
    )
