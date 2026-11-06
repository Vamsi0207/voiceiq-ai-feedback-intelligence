"""Explicit trusted model download, separate from normal API startup."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.ml.pipeline import sentence_model

if __name__ == "__main__":
    model = sentence_model()
    vectors = model.encode(
        [
            "UPI transfer failed but money deducted",
            "Payment unsuccessful, balance reduced",
        ],
        normalize_embeddings=True,
    )
    print("Sentence-transformer loaded; embedding shape:", vectors.shape)
