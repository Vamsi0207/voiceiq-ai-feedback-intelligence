import math
from sqlalchemy import select, func, delete
from app.models.entities import ComplaintCluster, Complaint, GeneratedInsight
from app.ai.providers import get_provider, ProviderError

SEVERITY = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
SOLUTIONS = {
    "UPI & Payments": (
        "Investigate payment reconciliation and make reversal status visible.",
        "Failed-payment reversal time and unresolved debit rate",
    ),
    "Credit Cards": (
        "Audit disputed card entries and surface dispute progress.",
        "Duplicate-charge incidence and dispute resolution time",
    ),
    "Account Access": (
        "Review sign-in and recovery journeys with affected customers.",
        "Successful recovery rate and time to restore access",
    ),
    "Mobile Banking": (
        "Reproduce reported stability issues on affected devices.",
        "Crash-free sessions and task completion rate",
    ),
    "Loans": (
        "Review repayment transparency and application status updates.",
        "Repayment-query rate and application turnaround",
    ),
    "Customer Support": (
        "Audit unresolved cases and improve ownership of follow-ups.",
        "First response time and reopened ticket rate",
    ),
    "Fraud & Security": (
        "Escalate reported unauthorized activity to trained reviewers.",
        "Time to human triage and verified incident resolution",
    ),
    "Other": (
        "Review branch and accessibility feedback with service owners.",
        "Feedback resolution rate and customer satisfaction",
    ),
}


def generate(db, force=False):
    cached = db.scalars(select(GeneratedInsight)).all()
    if cached and not force:
        return cached, []
    clusters = db.scalars(
        select(ComplaintCluster)
        .order_by(ComplaintCluster.complaint_count.desc())
        .limit(12)
    ).all()
    if not clusters:
        return [], []
    provider = get_provider()
    warnings = []
    results = []
    latest = db.scalar(select(func.max(Complaint.created_at)))
    max_count = max(c.complaint_count for c in clusters)
    # Build all results before replacing the last cache.
    for index, cluster in enumerate(clusters):
        members = db.scalars(
            select(Complaint)
            .where(Complaint.cluster_id == cluster.id)
            .order_by(Complaint.id)
        ).all()
        evidence = [
            dict(complaint_id=c.complaint_id, text=c.complaint_text[:700])
            for c in members[:8]
        ]
        severity = sum(SEVERITY[c.urgency] for c in members) / len(members) / 4
        recency = math.exp(
            -max(0, (latest - max(c.created_at for c in members)).days) / 30
        )
        score = round(
            100 * (0.45 * len(members) / max_count + 0.35 * severity + 0.20 * recency),
            1,
        )
        solution, metric = SOLUTIONS[cluster.dominant_category]
        result = dict(
            title=cluster.representative_label,
            description=cluster.summary,
            related_category=cluster.dominant_category,
            supporting_complaint_ids=[e["complaint_id"] for e in evidence],
            frequency=len(members),
            urgency=max((c.urgency for c in members), key=SEVERITY.get),
            priority="High" if score >= 70 else "Medium" if score >= 45 else "Low",
            priority_score=score,
            recommendation=solution
            + " Expected benefit: clearer issue resolution and fewer repeat customer contacts.",
            success_metric=metric,
            reasoning="Calculated from 45% relative frequency, 35% mean severity, 20% recency. Suggested intervention requires human investigation.",
            provider="deterministic",
            model_name="extractive-rules-v1",
        )
        # Bound synchronous external calls to three; remaining insights still work without LLM.
        if provider and index < 3:
            try:
                ai = provider.generate(evidence)
                cluster.summary = f"AI summary ({provider.name}/{provider.model}): {ai.problem} Symptoms: {ai.symptoms} Impact: {ai.impact} Hypothesis (unconfirmed): {ai.hypothesis} Evidence: {', '.join(ai.evidence_ids)}"
                result.update(
                    description=f"{ai.problem}\nSymptoms: {ai.symptoms}\nImpact: {ai.impact}\nHypothesis (unconfirmed): {ai.hypothesis}",
                    recommendation=ai.recommendation
                    + " Expected benefit: "
                    + ai.benefit,
                    success_metric=ai.success_metric,
                    supporting_complaint_ids=ai.evidence_ids,
                    provider=provider.name,
                    model_name=provider.model,
                )
            except Exception as exc:
                warnings.append(
                    f"{provider.name} generation failed ({exc.code if isinstance(exc, ProviderError) else type(exc).__name__}); deterministic evidence summary retained."
                )
        results.append(GeneratedInsight(**result))
    db.execute(delete(GeneratedInsight))
    db.add_all(results)
    db.commit()
    return results, warnings
