import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
    silhouette_score,
)
from app.ml.pipeline import load_models, group, embed
from app.core.config import ROOT, ARTIFACTS


def evaluate():
    train = pd.read_csv(ROOT / "data/sample_complaints.csv")
    test = pd.read_csv(ROOT / "data/evaluation/heldout.csv")
    assert not set(train.complaint_text) & set(test.complaint_text), (
        "Exact train/evaluation leakage"
    )
    m = load_models()
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_version": m["version"],
        "training_records": len(train),
        "evaluation_records": len(test),
        "dataset": "independent-phrase synthetic heldout; not real-world validation",
    }
    for field in ["category", "sentiment"]:
        predicted = m[field].predict(test.complaint_text)
        labels = m[field].classes_.tolist()
        p, r, f, _ = precision_recall_fscore_support(
            test[field], predicted, average="macro", zero_division=0
        )
        result[field] = {
            "accuracy": accuracy_score(test[field], predicted),
            "macro_precision": p,
            "macro_recall": r,
            "macro_f1": f,
            "per_class": classification_report(
                test[field], predicted, output_dict=True, zero_division=0
            ),
            "labels": labels,
            "confusion_matrix": confusion_matrix(
                test[field], predicted, labels=labels
            ).tolist(),
        }
    sample = train.sample(300, random_state=42)
    texts = sample.complaint_text.tolist()
    labels, method = group(texts)
    from collections import Counter

    counts = Counter(labels)
    groups = [i for i in counts if i != -1]
    result["clustering"] = {
        "method": method,
        "sample_size": len(texts),
        "clusters": len(groups),
        "noise_records": counts[-1],
        "examples": [
            {
                "size": counts[i],
                "texts": [
                    t for t, assigned_label in zip(texts, labels) if assigned_label == i
                ][:3],
            }
            for i in groups[:5]
        ],
        "limitation": "Synthetic repetition encourages tight groups. Qualitative human review is required.",
    }
    # Silhouette only meaningful for 2+ non-noise groups and fewer groups than members.
    keep = [i for i, assigned_label in enumerate(labels) if assigned_label != -1]
    if 1 < len(groups) < len(keep):
        vectors, _ = embed([texts[i] for i in keep])
        result["clustering"]["silhouette_cosine"] = float(
            silhouette_score(vectors, [labels[i] for i in keep], metric="cosine")
        )
    (ARTIFACTS / "evaluation.json").write_text(json.dumps(result, indent=2))
    (ROOT / "data/evaluation/results.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in ["model_version", "evaluation_records"]}))
    print(
        "Category macro F1:",
        result["category"]["macro_f1"],
        "Sentiment macro F1:",
        result["sentiment"]["macro_f1"],
    )
    return result


if __name__ == "__main__":
    evaluate()
