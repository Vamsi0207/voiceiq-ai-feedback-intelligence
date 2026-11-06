from datetime import date, datetime, time
from collections import Counter
from fastapi import HTTPException
from sqlalchemy import select
from app.models.entities import Complaint, ComplaintCluster


def filtered(
    q="",
    category="",
    sentiment="",
    urgency="",
    source="",
    date_from: date | None = None,
    date_to: date | None = None,
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(422, "date_from must be before date_to")
    stmt = select(Complaint)
    for field, value in [
        (Complaint.category, category),
        (Complaint.sentiment, sentiment),
        (Complaint.urgency, urgency),
        (Complaint.source, source),
    ]:
        if value:
            stmt = stmt.where(field == value)
    if q:
        stmt = stmt.where(
            Complaint.complaint_text.contains(q, autoescape=True)
            | Complaint.complaint_id.contains(q, autoescape=True)
        )
    if date_from:
        stmt = stmt.where(Complaint.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        stmt = stmt.where(Complaint.created_at <= datetime.combine(date_to, time.max))
    return stmt


def overview(db, filters):
    rows = db.scalars(filtered(**filters)).all()
    total = len(rows)
    categories = Counter(r.category or "Pending" for r in rows)
    sentiments = Counter(r.sentiment or "Pending" for r in rows)
    urgencies = Counter(r.urgency or "Pending" for r in rows)
    counts = Counter(r.cluster_id for r in rows if r.cluster_id is not None)
    clusters = (
        db.scalars(
            select(ComplaintCluster).where(ComplaintCluster.id.in_(counts))
        ).all()
        if counts
        else []
    )
    return dict(
        total=total,
        negative_percentage=round(sentiments["Negative"] / total * 100, 1)
        if total
        else 0,
        elevated_urgency=urgencies["High"] + urgencies["Critical"],
        largest_category=categories.most_common(1)[0][0] if categories else "—",
        recurring_clusters=sum(v >= 3 for v in counts.values()),
        categories=dict(categories),
        sentiments=dict(sentiments),
        urgencies=dict(urgencies),
        sources=list(db.scalars(select(Complaint.source).distinct())),
        clusters=[
            dict(id=c.id, label=c.representative_label, count=counts[c.id])
            for c in sorted(clusters, key=lambda c: counts[c.id], reverse=True)[:6]
        ],
        pending=sum(r.processing_status != "completed" for r in rows),
    )


def trends(db, filters):
    counts = Counter(
        r.created_at.date().isoformat() for r in db.scalars(filtered(**filters))
    )
    return [dict(date=k, count=v) for k, v in sorted(counts.items())]


def executive_overview(db, f):
    stats = overview(db, f)
    times = trends(db, f)
    midpoint = len(times) // 2
    recent = sum(t["count"] for t in times[midpoint:])
    earlier = sum(t["count"] for t in times[:midpoint])
    return dict(
        provider="deterministic",
        model="sql-extractive-v1",
        summary=f"{stats['total']} selected records; {stats['negative_percentage']}% negative. {stats['elevated_urgency']} high or critical. Leading category: {stats['largest_category']}. {stats['recurring_clusters']} recurring groups. Investigate elevated urgency evidence before deciding product priorities.",
        top_categories=sorted(
            stats["categories"].items(), key=lambda x: x[1], reverse=True
        )[:3],
        top_issues=stats["clusters"][:3],
        trend=dict(
            earlier_active_days_count=earlier,
            later_active_days_count=recent,
            interpretation="Counts split by active dates, not proof of an emerging trend; inspect the daily chart.",
        ),
    )
