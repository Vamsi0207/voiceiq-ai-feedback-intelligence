from datetime import date
from collections import Counter
import json
from typing import Annotated, Literal
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks,
    Query,
)
from fastapi.responses import Response
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import Complaint, ComplaintCluster, GeneratedInsight, Job
from app.schemas.contracts import (
    ComplaintOut,
    ComplaintPage,
    BatchOut,
    JobOut,
    InsightOut,
    ClusterOut,
    Overview,
    TrendPoint,
)
from app.services.ingestion import ingest
from app.services.analytics import filtered, overview, trends, executive_overview
from app.services.analysis import analysis_lock, run_analysis, pending_condition
from app.services.insights import generate
from app.ai.providers import get_provider, configuration_issue
from app.core.config import settings, ARTIFACTS
from app.ml.pipeline import load_models

router = APIRouter(prefix="/api")
DB = Annotated[Session, Depends(get_db)]


def filters(
    q: str = Query("", max_length=200),
    category: str = "",
    sentiment: str = "",
    urgency: str = "",
    source: str = "",
    date_from: date | None = None,
    date_to: date | None = None,
):
    return dict(
        q=q,
        category=category,
        sentiment=sentiment,
        urgency=urgency,
        source=source,
        date_from=date_from,
        date_to=date_to,
    )


Filters = Annotated[dict, Depends(filters)]


@router.get("/health")
def health(db: DB):
    db.execute(select(1))
    return {"status": "ok", "version": "1.0.0"}


@router.get("/complaints/example")
def example():
    return Response(
        "complaint_id,complaint_text,created_at,customer_id,source\nEXAMPLE-001,UPI payment failed but money deducted. Please investigate.,2026-10-15,SYN-001,Support ticket\nEXAMPLE-002,Mobile banking app keeps crashing on login.,2026-10-16,SYN-002,App review\nEXAMPLE-003,Thank you for excellent customer support.,2026-10-17,SYN-003,Survey\n",
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=voiceiq-example.csv"},
    )


@router.post("/complaints/upload", response_model=BatchOut)
async def upload(db: DB, file: UploadFile = File(...)):
    content = await file.read(5 * 1024 * 1024 + 1)
    return ingest(db, content, file.filename or "")


@router.get("/complaints", response_model=ComplaintPage)
def complaints(
    db: DB,
    f: Filters,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    sort: Literal["created_at", "urgency", "confidence"] = "created_at",
    direction: Literal["asc", "desc"] = "desc",
):
    stmt = filtered(**f)
    count = db.scalar(select(func.count()).select_from(stmt.subquery()))
    column = (
        case(
            {"Low": 1, "Medium": 2, "High": 3, "Critical": 4},
            value=Complaint.urgency,
            else_=0,
        )
        if sort == "urgency"
        else getattr(Complaint, sort)
    )
    stmt = (
        stmt.order_by(
            column.desc() if direction == "desc" else column.asc(), Complaint.id
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return dict(
        items=db.scalars(stmt).all(), total=count, page=page, page_size=page_size
    )


@router.post("/complaints/analyze", status_code=202, response_model=JobOut)
def analyze(db: DB, tasks: BackgroundTasks):
    try:
        load_models()
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc)) from exc
    if not analysis_lock.acquire(blocking=False):
        raise HTTPException(409, "Analysis already running")
    try:
        job = Job(
            total=db.scalar(
                select(func.count()).select_from(Complaint).where(pending_condition())
            )
        )
        db.add(job)
        db.commit()
        tasks.add_task(run_analysis, job.id)
        return job
    except Exception:
        analysis_lock.release()
        raise


@router.get("/complaints/{id}", response_model=ComplaintOut)
def complaint(id: int, db: DB):
    row = db.get(Complaint, id)
    if not row:
        raise HTTPException(404, "Complaint not found")
    return row


@router.get("/jobs/{id}", response_model=JobOut)
def job(id: int, db: DB):
    row = db.get(Job, id)
    if not row:
        raise HTTPException(404, "Job not found")
    return row


@router.get("/dashboard/overview", response_model=Overview)
def dashboard(db: DB, f: Filters):
    return overview(db, f)


@router.get("/dashboard/trends", response_model=list[TrendPoint])
def trend(db: DB, f: Filters):
    return trends(db, f)


def cluster_result(db, c):
    members = db.scalars(
        select(Complaint).where(Complaint.cluster_id == c.id).order_by(Complaint.id)
    ).all()
    return dict(
        id=c.id,
        representative_label=c.representative_label,
        complaint_count=c.complaint_count,
        dominant_category=c.dominant_category,
        summary=c.summary,
        method=c.method,
        created_at=c.created_at,
        representative_complaint=members[0],
        sentiment_breakdown=dict(Counter(r.sentiment for r in members)),
    )


@router.get("/clusters", response_model=list[ClusterOut])
def clusters(db: DB):
    return [
        cluster_result(db, c)
        for c in db.scalars(
            select(ComplaintCluster).order_by(ComplaintCluster.complaint_count.desc())
        )
    ]


@router.get("/clusters/{id}")
def cluster(id: int, db: DB):
    c = db.get(ComplaintCluster, id)
    if not c:
        raise HTTPException(404, "Cluster not found")
    result = ClusterOut.model_validate(cluster_result(db, c)).model_dump(mode="json")
    result["members"] = [
        ComplaintOut.model_validate(r).model_dump(mode="json")
        for r in db.scalars(
            select(Complaint)
            .where(Complaint.cluster_id == id)
            .order_by(Complaint.id)
            .limit(100)
        )
    ]
    result["members_limit"] = 100
    return result


@router.get("/insights", response_model=list[InsightOut])
def insights(db: DB, category: str = "", priority: str = ""):
    stmt = select(GeneratedInsight)
    if category:
        stmt = stmt.where(GeneratedInsight.related_category == category)
    if priority:
        stmt = stmt.where(GeneratedInsight.priority == priority)
    return db.scalars(stmt.order_by(GeneratedInsight.priority_score.desc())).all()


@router.post("/insights/generate")
def generate_insights(db: DB, force: bool = False):
    if analysis_lock.locked():
        raise HTTPException(409, "Wait for analysis to complete")
    if not analysis_lock.acquire(blocking=False):
        raise HTTPException(409, "Insight generation already running")
    try:
        rows, warnings = generate(db, force)
        return dict(
            items=[InsightOut.model_validate(r).model_dump(mode="json") for r in rows],
            warnings=warnings,
        )
    finally:
        analysis_lock.release()


@router.get("/evaluation/summary")
def evaluation():
    path = ARTIFACTS / "evaluation.json"
    if not path.exists():
        raise HTTPException(
            404, "Run python scripts/evaluate.py to calculate evaluation"
        )
    return json.loads(path.read_text())


@router.get("/settings/ai-status")
def ai_status():
    p = get_provider()
    return dict(
        configured=p is not None,
        provider=p.name if p else "deterministic",
        model=p.model if p else "extractive-rules-v1",
        embedding_mode=settings.embedding_mode,
        embedding_model=settings.embedding_model
        if settings.embedding_mode == "sentence-transformer"
        else "TF-IDF lexical fallback",
        message=configuration_issue()
        or "Provider configured; live access is not verified by this status."
        if p
        else (
            configuration_issue()
            or "No LLM configured. Local ML, clustering and deterministic summaries are available."
        ),
    )


@router.get("/dashboard/executive-summary")
def executive_summary(db: DB, f: Filters):
    return executive_overview(db, f)
