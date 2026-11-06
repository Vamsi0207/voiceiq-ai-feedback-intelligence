import { useApi } from "../hooks/useApi";
import { Badge, ErrorBox, Loading, Modal } from "./UI";
import type { Complaint } from "../types";
export function ComplaintDetail({
  id,
  onClose,
}: {
  id: number;
  onClose: () => void;
}) {
  const { data: c, error, loading } = useApi<Complaint>("/complaints/" + id);
  return (
    <Modal title={c?.complaint_id || "Complaint details"} onClose={onClose}>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : (
        c && (
          <>
            <div className="tag-row">
              <Badge>{c.category}</Badge>
              <Badge>{c.sentiment}</Badge>
              <Badge>{c.urgency}</Badge>
            </div>
            <blockquote>{c.complaint_text}</blockquote>
            <dl className="details">
              {Object.entries({
                Source: c.source,
                "Received (UTC)": c.created_at,
                Customer: c.customer_id || "Not supplied",
                "Category confidence":
                  c.confidence == null
                    ? "Pending"
                    : `${(c.confidence * 100).toFixed(1)}%`,
                "Sentiment confidence":
                  c.sentiment_confidence == null
                    ? "Pending"
                    : `${(c.sentiment_confidence * 100).toFixed(1)}%`,
                "Urgency reason": c.urgency_reason || "Pending",
                Status: c.processing_status,
                Cluster: c.cluster_id || "Unclustered",
                Model: c.model_version || "Not processed",
                "Processed (UTC)": c.processed_at || "Pending",
              }).map(([k, v]) => (
                <div key={k}>
                  <dt>{k}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
            <p className="notice">
              Urgency supports human prioritization. It is not a fraud
              determination.
            </p>
          </>
        )
      )}
    </Modal>
  );
}
