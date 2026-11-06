import { useState } from "react";
import { Sparkles, ArrowUpRight, Target } from "lucide-react";
import { useApi } from "../hooks/useApi";
import { api, categories, query } from "../services/api";
import {
  Heading,
  Badge,
  Panel,
  Loading,
  ErrorBox,
  Empty,
} from "../components/UI";
import type { Insight, Page } from "../types";
import { ComplaintDetail } from "../components/ComplaintDetail";
export function Insights({
  revision,
  onChange,
  notify,
}: {
  revision: number;
  onChange: () => void;
  notify: (s: string) => void;
}) {
  const [category, setCategory] = useState(""),
    [priority, setPriority] = useState(""),
    [busy, setBusy] = useState(false),
    [failure, setFailure] = useState(""),
    [selected, setSelected] = useState<number>();
  const executive = useApi<{ summary: string }>(
    "/dashboard/executive-summary",
    revision,
  );
  const { data, error, loading } = useApi<Insight[]>(
    "/insights" + query({ category, priority }),
    revision,
  );
  async function generate() {
    setBusy(true);
    setFailure("");
    try {
      const r = await api<{ items: Insight[]; warnings: string[] }>(
        "/insights/generate?force=true",
        { method: "POST" },
      );
      onChange();
      notify(
        r.warnings.length
          ? r.warnings.join(" ")
          : `Generated ${r.items.length} evidence-linked insights`,
      );
    } catch (e) {
      setFailure((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function evidence(id: string) {
    try {
      const r = await api<Page>("/complaints" + query({ q: id }));
      const c = r.items.find((c) => c.complaint_id === id);
      if (c) setSelected(c.id);
      else setFailure("Evidence record is no longer available");
    } catch (e) {
      setFailure((e as Error).message);
    }
  }
  return (
    <>
      <Heading
        eyebrow="EVIDENCE INTO OPPORTUNITY"
        title="Product insights"
        description="Prioritize customer problems with a transparent, calculated score."
        action={
          <button className="button primary" disabled={busy} onClick={generate}>
            <Sparkles size={16} />
            {busy ? "Generating…" : "Generate insights"}
          </button>
        }
      />
      <div className="notice">
        Priority score = 45% relative frequency + 35% severity + 20% recency.
        Recommendations are proposals for human review.
      </div>
      {executive.data && (
        <Panel
          title="Executive overview"
          subtitle="Calculated statistics · deterministic summary"
        >
          <p>{executive.data.summary}</p>
        </Panel>
      )}
      <div className="toolbar">
        <select
          aria-label="Insight category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        <select
          aria-label="Insight priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        >
          <option value="">All priorities</option>
          {["High", "Medium", "Low"].map((p) => (
            <option key={p}>{p}</option>
          ))}
        </select>
      </div>
      {failure && <ErrorBox message={failure} />}
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : !data?.length ? (
        <Empty text="Generate insights after analysis. Results are cached for browsing; Generate insights explicitly refreshes them." />
      ) : (
        <div className="insight-list">
          {data.map((i) => (
            <Panel key={i.id} title={i.title} subtitle={i.related_category}>
              <div className="insight-body">
                <div>
                  <div className="tag-row">
                    <Badge>{i.priority}</Badge>
                    <span>{i.frequency} complaints</span>
                    <Badge>{i.urgency}</Badge>
                  </div>
                  <p className="summary">{i.description}</p>
                  <h3>Suggested improvement</h3>
                  <p>{i.recommendation}</p>
                  <div className="metric">
                    <Target size={17} />
                    <span>
                      <strong>Measure success</strong>
                      {i.success_metric}
                    </span>
                  </div>
                  <h3>Traceable evidence</h3>
                  <div className="evidence-chips">
                    {i.supporting_complaint_ids.map((id) => (
                      <button key={id} onClick={() => evidence(id)}>
                        {id}
                        <ArrowUpRight size={13} />
                      </button>
                    ))}
                  </div>
                </div>
                <aside className="score">
                  <small>PRIORITY SCORE</small>
                  <strong>{i.priority_score}</strong>
                  <span>out of 100</span>
                  <p>{i.reasoning}</p>
                  <Badge>{i.provider}</Badge>
                  <small>{i.model_name}</small>
                </aside>
              </div>
            </Panel>
          ))}
        </div>
      )}
      {selected && (
        <ComplaintDetail id={selected} onClose={() => setSelected(undefined)} />
      )}
    </>
  );
}
