from pathlib import Path
import hashlib
import numpy as np
from app.ml.features import normalize_text, sentiment_features
from app.ml.pipeline import load_models

HELDOUT_SHA256 = "c8680baf9ce0d1a384b0d8e0bf84d97f795cb3ce0c08c82a5e881fa0a9de09bc"


def test_frozen_evaluation_bytes():
    path = Path(__file__).resolve().parents[2] / "data/evaluation/heldout.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == HELDOUT_SHA256


def test_normalization_removes_synthetic_identifiers():
    assert (
        normalize_text(
            "UPI failed. This concerns my salary banking, reference SYN-1234."
        )
        == "upi failed."
    )
    assert normalize_text("ＦＡＩＬＥＤ   payment") == "failed payment"


def test_independent_lexicon_features_and_negation():
    scores = sentiment_features(
        ["This service is excellent!", "This service is not excellent."]
    )
    assert scores.shape == (2, 8)
    assert scores[0, 3] > scores[1, 3]
    assert np.isfinite(scores).all()


def test_models_record_feature_and_training_provenance():
    m = load_models()
    assert m["training_metadata"]["feature_version"] == "word-char-vader-v2"
    assert len(m["training_metadata"]["training_sha256"]) == 64
    assert m["training_metadata"]["training_records"] == 2400


def test_model_upgrade_reprocesses_completed_records(client, monkeypatch):
    from app.services import analysis
    from test_workflow import upload, dataset

    upload(client, dataset())
    first = client.post("/api/complaints/analyze").json()
    assert client.get("/api/jobs/" + str(first["id"])).json()["completed"] == 7
    original = analysis.predict
    monkeypatch.setattr(analysis, "load_models", lambda: {"version": "upgraded-test"})

    def upgraded(texts):
        result = original(texts)
        for row in result:
            row["model_version"] = "upgraded-test"
        return result

    monkeypatch.setattr(analysis, "predict", upgraded)
    job = client.post("/api/complaints/analyze").json()
    assert client.get("/api/jobs/" + str(job["id"])).json()["completed"] == 7
    assert all(
        c["model_version"] == "upgraded-test"
        for c in client.get("/api/complaints").json()["items"]
    )
