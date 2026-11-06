import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Layers, ArrowUpRight } from "lucide-react";
import { useApi } from "../hooks/useApi";
import {
  Heading,
  Badge,
  Panel,
  Modal,
  Loading,
  ErrorBox,
  Empty,
} from "../components/UI";
import { ComplaintDetail } from "../components/ComplaintDetail";
import type { Cluster } from "../types";
function ClusterDetail({ id, onClose }: { id: number; onClose: () => void }) {
  const { data, error, loading } = useApi<Cluster>("/clusters/" + id);
  const [selected, setSelected] = useState<number>();
  return (
    <>
      <Modal title="Recurring issue evidence" onClose={onClose}>
        {loading ? (
          <Loading />
        ) : error ? (
          <ErrorBox message={error} />
        ) : (
          data && (
            <>
              <h3>{data.representative_label}</h3>
              <div className="tag-row">
                <Badge>{data.dominant_category}</Badge>
                <span>{data.complaint_count} complaints</span>
              </div>
              <p className="summary">{data.summary}</p>
              <p className="muted">
                Grouping: {data.method}.{" "}
                {Object.entries(data.sentiment_breakdown)
                  .map(([k, v]) => `${k}: ${v}`)
                  .join(" · ")}
              </p>
              <h3>Supporting complaints</h3>
              <p className="muted">
                Showing up to {data.members_limit} records.
              </p>
              {data.members?.map((c) => (
                <button
                  key={c.id}
                  className="evidence-row"
                  onClick={() => setSelected(c.id)}
                >
                  <strong>{c.complaint_id}</strong>
                  <span>{c.complaint_text}</span>
                  <ArrowUpRight size={15} />
                </button>
              ))}
            </>
          )
        )}
      </Modal>
      {selected && (
        <ComplaintDetail id={selected} onClose={() => setSelected(undefined)} />
      )}
    </>
  );
}
export function Clusters({ revision }: { revision: number }) {
  const { data, error, loading } = useApi<Cluster[]>("/clusters", revision);
  const [params, setParams] = useSearchParams();
  const selected = Number(params.get("open")) || undefined;
  return (
    <>
      <Heading
        eyebrow="FROM INDIVIDUAL VOICES TO SHARED PROBLEMS"
        title="Recurring issues"
        description="Find related feedback and inspect the customer evidence."
      />
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : !data?.length ? (
        <Empty text="Analyze imported feedback to find recurring issues. Noise stays unclustered." />
      ) : (
        <div className="issue-grid">
          {data.map((c) => (
            <Panel
              key={c.id}
              title={c.representative_label}
              subtitle={c.dominant_category}
            >
              <div className="cluster-count">
                <Layers size={20} />
                <strong>{c.complaint_count}</strong>
                <span>related complaints</span>
              </div>
              <p className="summary">{c.summary}</p>
              <div className="tag-row">
                {Object.entries(c.sentiment_breakdown).map(([name, count]) => (
                  <span key={name}>
                    <Badge>{name}</Badge> {count}
                  </span>
                ))}
              </div>
              <div className="card-footer">
                <small>{c.method}</small>
                <button
                  className="text-button"
                  onClick={() => setParams({ open: String(c.id) })}
                >
                  Explore evidence <ArrowUpRight size={15} />
                </button>
              </div>
            </Panel>
          ))}
        </div>
      )}
      {selected && (
        <ClusterDetail id={selected} onClose={() => setParams({})} />
      )}
    </>
  );
}
