from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base


def utcnow():
    return datetime.now(timezone.utc)


class AnalysisBatch(Base):
    __tablename__ = "analysis_batches"
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    total_records: Mapped[int] = mapped_column(default=0)
    successful_records: Mapped[int] = mapped_column(default=0)
    failed_records: Mapped[int] = mapped_column(default=0)
    duplicate_records: Mapped[int] = mapped_column(default=0)
    errors: Mapped[list] = mapped_column(JSON, default=list)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    status: Mapped[str] = mapped_column(default="completed")


class ComplaintCluster(Base):
    __tablename__ = "complaint_clusters"
    id: Mapped[int] = mapped_column(primary_key=True)
    representative_label: Mapped[str] = mapped_column(Text)
    complaint_count: Mapped[int] = mapped_column(default=0)
    dominant_category: Mapped[str] = mapped_column(String(80))
    summary: Mapped[str] = mapped_column(Text)
    method: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Complaint(Base):
    __tablename__ = "complaints"
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    customer_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    complaint_text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(80), default="Unknown", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    urgency: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    sentiment_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    urgency_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    processing_status: Mapped[str] = mapped_column(default="pending", index=True)
    cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("complaint_clusters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("analysis_batches.id"), nullable=True
    )
    model_version: Mapped[str | None] = mapped_column(String(80), nullable=True)


class GeneratedInsight(Base):
    __tablename__ = "generated_insights"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    related_category: Mapped[str] = mapped_column(String(80), index=True)
    supporting_complaint_ids: Mapped[list] = mapped_column(JSON)
    frequency: Mapped[int] = mapped_column(Integer)
    urgency: Mapped[str] = mapped_column(String(20))
    priority: Mapped[str] = mapped_column(String(20), index=True)
    priority_score: Mapped[float] = mapped_column(Float)
    recommendation: Mapped[str] = mapped_column(Text)
    success_metric: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(30))
    model_name: Mapped[str] = mapped_column(String(120))
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(default="queued")
    completed: Mapped[int] = mapped_column(default=0)
    total: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
