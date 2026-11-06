import { useApi } from "../hooks/useApi";
import { Heading, Panel, Loading, ErrorBox } from "../components/UI";
import type { Evaluation as EvaluationData } from "../types";
const percent = (n: number) => (n * 100).toFixed(1) + "%";
export function Evaluation({ revision }: { revision: number }) {
  const {
    data: d,
    error,
    loading,
  } = useApi<EvaluationData>("/evaluation/summary", revision);
  return (
    <>
      <Heading
        eyebrow="MEASURED, NOT ASSUMED"
        title="Model evaluation"
        description="A reproducible benchmark with visible strengths and limitations."
      />
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : (
        d && (
          <>
            <p className="notice">
              {d.dataset}. Synthetic evaluation does not establish performance
              on real customer data.
            </p>
            <div className="kpis">
              {[
                ["Category accuracy", d.category.accuracy],
                ["Category macro F1", d.category.macro_f1],
                ["Sentiment accuracy", d.sentiment.accuracy],
                ["Sentiment macro F1", d.sentiment.macro_f1],
              ].map(([k, v]) => (
                <div className="kpi" key={k}>
                  <div className="kpi-label">{k}</div>
                  <strong>{percent(Number(v))}</strong>
                  <small>Held-out independent phrasing</small>
                </div>
              ))}
            </div>
            <Panel
              title="Category performance"
              subtitle={`${d.training_records} training records · ${d.evaluation_records} evaluation records · model ${d.model_version}`}
            >
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Precision</th>
                      <th>Recall</th>
                      <th>F1</th>
                      <th>Support</th>
                    </tr>
                  </thead>
                  <tbody>
                    {d.category.labels.map((c) => {
                      const m = d.category.per_class[c];
                      return (
                        <tr key={c}>
                          <td>{c}</td>
                          <td>{percent(m.precision)}</td>
                          <td>{percent(m.recall)}</td>
                          <td>{percent(m["f1-score"])}</td>
                          <td>{m.support}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </Panel>
            <Panel
              title="Confusion matrix"
              subtitle="Rows are actual classes; columns are predicted classes in the order below."
            >
              <div className="table-scroll">
                <table className="matrix">
                  <thead>
                    <tr>
                      <th>Actual / Predicted</th>
                      {d.category.labels.map((c, i) => (
                        <th key={c} title={c}>
                          {i + 1}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {d.category.confusion_matrix.map((r, i) => (
                      <tr key={i}>
                        <td>
                          {i + 1}. {d.category.labels[i]}
                        </td>
                        {r.map((v, j) => (
                          <td
                            key={j}
                            style={{
                              background: v
                                ? `rgba(57,115,232,${Math.min(0.65, 0.08 + v / 20)})`
                                : undefined,
                            }}
                          >
                            {v}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>
            <Panel
              title="Clustering diagnostics"
              subtitle={d.clustering.method}
            >
              <div className="tag-row">
                <span>{d.clustering.sample_size} sampled records</span>
                <span>{d.clustering.clusters} groups</span>
                <span>{d.clustering.noise_records} noise records</span>
                <span>
                  Silhouette:{" "}
                  {d.clustering.silhouette_cosine?.toFixed(3) || "Not defined"}
                </span>
              </div>
              <p className="notice">{d.clustering.limitation}</p>
              {d.clustering.examples.map((g, i) => (
                <details key={i}>
                  <summary>
                    Group {i + 1} · {g.size} records
                  </summary>
                  {g.texts.map((t) => (
                    <blockquote key={t}>{t}</blockquote>
                  ))}
                </details>
              ))}
            </Panel>
            <p className="muted">
              Evaluated {d.generated_at}. Mixed sentiment, unfamiliar
              terminology, negation, spelling and code switching need real-world
              review.
            </p>
          </>
        )
      )}
    </>
  );
}
