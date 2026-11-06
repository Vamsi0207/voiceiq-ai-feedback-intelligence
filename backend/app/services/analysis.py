import logging
from collections import Counter
from threading import Lock
from sqlalchemy import select, update, delete, or_
from app.database.session import SessionLocal
from app.models.entities import (
    Complaint,
    ComplaintCluster,
    GeneratedInsight,
    Job,
    utcnow,
)
from app.ml.pipeline import predict, group, load_models

logger = logging.getLogger("voiceiq.analysis")
analysis_lock = Lock()


def rebuild_clusters(db):
    rows = db.scalars(
        select(Complaint)
        .where(Complaint.processing_status == "completed")
        .order_by(Complaint.id)
    ).all()
    if not rows:
        return
    labels, method = group([r.complaint_text for r in rows])
    db.execute(update(Complaint).values(cluster_id=None))
    db.execute(delete(GeneratedInsight))
    db.execute(delete(ComplaintCluster))
    for label in sorted(set(labels) - {-1}):
        members = [
            r for r, assigned_label in zip(rows, labels) if assigned_label == label
        ]
        rep = members[0]
        title = rep.complaint_text.split(". ")[0][:120]
        cluster = ComplaintCluster(
            representative_label=title,
            complaint_count=len(members),
            dominant_category=Counter(r.category for r in members).most_common(1)[0][0],
            summary=f"Deterministic extractive summary: {len(members)} related records. Representative evidence [{rep.complaint_id}]: “{rep.complaint_text[:300]}”",
            method=method,
        )
        db.add(cluster)
        db.flush()
        for r in members:
            r.cluster_id = cluster.id
    db.commit()


def pending_condition():
    version = load_models()["version"]
    return or_(
        Complaint.processing_status != "completed",
        Complaint.model_version.is_(None),
        Complaint.model_version != version,
    )


def run_analysis(job_id):
    try:
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            job.status = "running"
            db.commit()
            rows = db.scalars(
                select(Complaint).where(pending_condition()).order_by(Complaint.id)
            ).all()
            job.total = len(rows)
            db.commit()
            for start in range(0, len(rows), 128):
                part = rows[start : start + 128]
                predictions = predict([r.complaint_text for r in part])
                for row, prediction in zip(part, predictions):
                    for key, value in prediction.items():
                        setattr(row, key, value)
                    row.processing_status = "completed"
                    row.processed_at = utcnow()
                job.completed += len(part)
                db.commit()
            rebuild_clusters(db)
            job.status = "completed"
            db.commit()
    except Exception as exc:
        logger.error(
            "analysis_failed",
            extra={"job_id": job_id, "error_type": type(exc).__name__},
        )
        with SessionLocal() as db:
            job = db.get(Job, job_id)
            job.status = "failed"
            job.error = (
                "Analysis failed ("
                + type(exc).__name__
                + "). Check model installation and embedding configuration; retry analysis."
            )
            db.commit()
    finally:
        analysis_lock.release()
