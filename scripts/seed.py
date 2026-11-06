"""Explicit idempotent seed; never removes user data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.database.session import Base, engine, SessionLocal
from app.services.ingestion import ingest
from app.services.analysis import analysis_lock, run_analysis
from app.services.insights import generate
from app.models.entities import Job
from app.core.config import ROOT

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        b = ingest(
            db,
            (ROOT / "data/sample_complaints.csv").read_bytes(),
            "sample_complaints.csv",
        )
        print("Imported", b.successful_records, "duplicates", b.duplicate_records)
        job = Job()
        db.add(job)
        db.commit()
        jid = job.id
    analysis_lock.acquire()
    run_analysis(jid)
    with SessionLocal() as db:
        job = db.get(Job, jid)
        if job.status != "completed":
            raise RuntimeError(job.error)
        insights, warnings = generate(db)
        print("Analysis complete; insights:", len(insights), warnings)
