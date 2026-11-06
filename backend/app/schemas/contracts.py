from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ComplaintOut(ORMModel):
    id: int
    complaint_id: str
    customer_id: str | None
    complaint_text: str
    category: str | None
    sentiment: str | None
    urgency: str | None
    confidence: float | None
    sentiment_confidence: float | None
    urgency_reason: str | None
    source: str
    created_at: datetime
    processed_at: datetime | None
    processing_status: str
    cluster_id: int | None
    model_version: str | None


class ComplaintPage(BaseModel):
    items: list[ComplaintOut]
    total: int
    page: int
    page_size: int


class BatchOut(ORMModel):
    id: int
    filename: str
    total_records: int
    successful_records: int
    duplicate_records: int
    failed_records: int
    errors: list[dict]
    status: str


class JobOut(ORMModel):
    id: int
    status: str
    completed: int
    total: int
    error: str | None


class InsightOut(ORMModel):
    id: int
    title: str
    description: str
    related_category: str
    supporting_complaint_ids: list[str]
    frequency: int
    urgency: str
    priority: str
    priority_score: float
    recommendation: str
    success_metric: str
    reasoning: str
    provider: str
    model_name: str
    generated_at: datetime


class AIProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem: str = Field(min_length=1, max_length=1500)
    symptoms: str = Field(min_length=1, max_length=1500)
    impact: str = Field(min_length=1, max_length=1500)
    hypothesis: str = Field(min_length=1, max_length=1000)
    recommendation: str = Field(min_length=1, max_length=1500)
    benefit: str = Field(min_length=1, max_length=1000)
    success_metric: str = Field(min_length=1, max_length=500)
    evidence_ids: list[str] = Field(min_length=1, max_length=8)


class ClusterOut(ORMModel):
    id: int
    representative_label: str
    complaint_count: int
    dominant_category: str
    summary: str
    method: str
    created_at: datetime
    representative_complaint: ComplaintOut
    sentiment_breakdown: dict[str, int]


class Overview(BaseModel):
    total: int
    negative_percentage: float
    elevated_urgency: int
    largest_category: str
    recurring_clusters: int
    categories: dict[str, int]
    sentiments: dict[str, int]
    urgencies: dict[str, int]
    sources: list[str]
    clusters: list[dict]
    pending: int


class TrendPoint(BaseModel):
    date: str
    count: int
