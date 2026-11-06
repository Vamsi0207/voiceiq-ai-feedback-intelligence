"""Opt-in real inference: explicit skip is not a passing semantic verification."""

import os
import pytest


@pytest.mark.skipif(
    os.environ.get("VOICEIQ_RUN_SEMANTIC") != "1",
    reason="Real MiniLM integration requires an explicitly downloaded model; network policy currently blocks its host",
)
def test_real_minilm_clustering_and_cache(tmp_path, monkeypatch):
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from app.ml import pipeline

    model = SentenceTransformer(
        pipeline.settings.embedding_model, device="cpu", local_files_only=True
    )
    monkeypatch.setattr(pipeline, "ARTIFACTS", tmp_path)
    monkeypatch.setattr(pipeline.settings, "embedding_mode", "sentence-transformer")
    monkeypatch.setattr(pipeline, "sentence_model", lambda: model)
    texts = [
        "UPI transfer failed but money deducted",
        "UPI payment failed and my money was deducted",
        "My money was deducted after a failed UPI transfer.",
        "Please change the parking hours at our local branch.",
    ]
    vectors, method = pipeline.embed(texts)
    assert vectors.shape == (4, 384)
    assert np.dot(vectors[0], vectors[1]) > np.dot(vectors[0], vectors[3]) + 0.1
    cached, _ = pipeline.embed(texts)
    np.testing.assert_array_equal(vectors, cached)
    labels, _ = pipeline.group(texts)
    assert labels[0] == labels[1] == labels[2] != -1
    assert labels[3] == -1
    assert method == pipeline.settings.embedding_model
