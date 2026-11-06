"""Report frozen-set release evaluation; never modifies or fits a model."""

import sys
import json
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import pandas as pd
from app.core.config import ROOT
from app.ml.pipeline import load_models
from app.ml.features import normalize_text

if __name__ == "__main__":
    base = json.loads((ROOT / "data/evaluation/baseline.json").read_text())
    current = json.loads((ROOT / "data/evaluation/results.json").read_text())
    test = pd.read_csv(ROOT / "data/evaluation/heldout.csv")
    train = pd.read_csv(ROOT / "data/sample_complaints.csv")
    m = load_models()
    assert (
        hashlib.sha256((ROOT / "data/sample_complaints.csv").read_bytes()).hexdigest()[
            :16
        ]
        == base["model_version"]
    )
    assert not set(test.complaint_text.map(normalize_text)) & set(
        train.complaint_text.map(normalize_text)
    )
    assert (
        hashlib.sha256((ROOT / "data/evaluation/heldout.csv").read_bytes()).hexdigest()
        == "c8680baf9ce0d1a384b0d8e0bf84d97f795cb3ce0c08c82a5e881fa0a9de09bc"
    )
    result = {
        "heldout_sha256": hashlib.sha256(
            (ROOT / "data/evaluation/heldout.csv").read_bytes()
        ).hexdigest(),
        "training_unchanged": True,
        "selection": "Candidate evaluated after grouped training validation. Frozen heldout used as release regression gate: retain baseline category, release improved sentiment. No subsequent parameter tuning or heldout examples added to training.",
        "metrics": {},
        "errors": {},
    }
    for task in ("category", "sentiment"):
        result["metrics"][task] = {
            metric: {
                "before": base[task][metric],
                "after": current[task][metric],
                "delta": current[task][metric] - base[task][metric],
            }
            for metric in ("accuracy", "macro_precision", "macro_recall", "macro_f1")
        }
        predictions = m[task].predict(test.complaint_text)
        result["errors"][task] = [
            {
                "complaint_id": r.complaint_id,
                "actual": getattr(r, task),
                "predicted": str(pred),
                "text": r.complaint_text,
            }
            for r, pred in zip(test.itertuples(), predictions)
            if getattr(r, task) != pred
        ]
    (ROOT / "data/evaluation/comparison.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result["metrics"], indent=2))
