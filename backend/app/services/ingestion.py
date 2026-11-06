import csv
import io
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.entities import Complaint, AnalysisBatch

REQUIRED = {"complaint_id", "complaint_text", "created_at"}


def ingest(db: Session, content: bytes, filename: str):
    if not filename.lower().endswith(".csv"):
        raise HTTPException(422, "Only .csv files are accepted")
    if not content or not content.strip():
        raise HTTPException(422, "CSV is empty")
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(413, "CSV exceeds 5 MB")
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")), strict=True)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise HTTPException(
                422, "Required columns: complaint_id, complaint_text, created_at"
            )
        rows = list(reader)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise HTTPException(422, "Malformed UTF-8 CSV") from exc
    if not rows:
        raise HTTPException(422, "CSV contains no data rows")
    if len(rows) > 10000:
        raise HTTPException(413, "Maximum 10,000 rows per upload")
    existing = set(db.scalars(select(Complaint.complaint_id)))
    accepted = []
    errors = []
    duplicates = 0
    for i, row in enumerate(rows, 2):
        try:
            if None in row:
                raise ValueError("Row has more fields than its header")
            cid = (row.get("complaint_id") or "").strip()
            text = " ".join((row.get("complaint_text") or "").split())
            if not 1 <= len(cid) <= 120:
                raise ValueError("complaint_id must be 1–120 characters")
            if not 1 <= len(text) <= 5000:
                raise ValueError("complaint_text must be 1–5,000 characters")
            try:
                date = datetime.fromisoformat(
                    (row.get("created_at") or "").replace("Z", "+00:00")
                )
            except ValueError:
                raise ValueError("created_at must be an ISO date or datetime")
            date = (
                date.replace(tzinfo=timezone.utc)
                if date.tzinfo is None
                else date.astimezone(timezone.utc)
            )
            source = (row.get("source") or "Unknown").strip()
            customer = (row.get("customer_id") or "").strip() or None
            if len(source) > 80 or (customer and len(customer) > 120):
                raise ValueError("source or customer_id is too long")
            if cid in existing:
                duplicates += 1
                continue
            existing.add(cid)
            accepted.append(
                Complaint(
                    complaint_id=cid,
                    complaint_text=text,
                    created_at=date.replace(tzinfo=None),
                    source=source,
                    customer_id=customer,
                )
            )
        except ValueError as exc:
            errors.append({"row": i, "reason": str(exc)})
    batch = AnalysisBatch(
        filename=filename[:255],
        total_records=len(rows),
        successful_records=len(accepted),
        failed_records=len(errors),
        duplicate_records=duplicates,
        errors=errors,
    )
    try:
        db.add(batch)
        db.flush()
        for complaint in accepted:
            complaint.batch_id = batch.id
        db.add_all(accepted)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return batch
