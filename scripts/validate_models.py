"""Select features on training-only grouped validation; never reads the heldout CSV."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score
from app.ml.features import build_classifier, normalize_text
from app.core.config import ROOT


def validate_models():
    train = pd.read_csv(ROOT / "data/sample_complaints.csv")
    # All duplicates of a complaint base stay in one fold for category;
    # all copies of an affect clause stay in one fold for sentiment.
    results = {}
    for task in ("category", "sentiment"):
        normalized = train.complaint_text.map(normalize_text)
        groups = (
            normalized.str.split(". ", regex=False).str[0]
            if task == "category"
            else normalized.str.split(". ", regex=False).str[-1]
        )
        groups = groups.str.replace("recieved", "received", regex=False).str.replace(
            "pls", "please", regex=False
        )
        task_result = {}
        for name, improved in [("baseline", False), ("candidate", True)]:
            scores = []
            for tr, dev in GroupKFold(n_splits=3).split(train, train[task], groups):
                model = build_classifier(task, improved)
                model.fit(train.complaint_text.iloc[tr], train[task].iloc[tr])
                scores.append(
                    f1_score(
                        train[task].iloc[dev],
                        model.predict(train.complaint_text.iloc[dev]),
                        average="macro",
                        zero_division=0,
                    )
                )
            task_result[name] = {
                "fold_macro_f1": scores,
                "mean_macro_f1": float(np.mean(scores)),
            }
        task_result["selected"] = (
            "candidate"
            if task_result["candidate"]["mean_macro_f1"]
            >= task_result["baseline"]["mean_macro_f1"]
            else "baseline"
        )
        results[task] = task_result
        print(task, task_result, flush=True)
    report = {
        "method": "3-fold grouped training-only validation, fixed model specification; heldout not loaded",
        "results": results,
    }
    (ROOT / "data/evaluation/training_validation.json").write_text(
        json.dumps(report, indent=2)
    )


if __name__ == "__main__":
    validate_models()
