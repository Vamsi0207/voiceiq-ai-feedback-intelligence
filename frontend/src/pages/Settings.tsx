import { useApi } from "../hooks/useApi";
import { Heading, Panel, Badge, Loading, ErrorBox } from "../components/UI";
import type { AIStatus } from "../types";
export function Settings() {
  const { data, error, loading } = useApi<AIStatus>("/settings/ai-status");
  return (
    <>
      <Heading
        eyebrow="TRANSPARENT BY DESIGN"
        title="Workspace settings"
        description="Understand how your feedback is processed and where it goes."
      />
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : (
        data && (
          <div className="settings-grid">
            <Panel
              title="AI integration"
              subtitle="Optional external generation"
            >
              <Badge>{data.configured ? "Configured" : "No-key mode"}</Badge>
              <p>{data.message}</p>
              <dl className="details">
                <div>
                  <dt>Provider</dt>
                  <dd>{data.provider}</dd>
                </div>
                <div>
                  <dt>Model</dt>
                  <dd>{data.model}</dd>
                </div>
              </dl>
              <p className="notice">
                Configure AI_PROVIDER and the matching API key and model in the
                backend environment, then restart. Keys are never entered or
                returned through this UI. See README for OpenAI and Gemini
                setup.
              </p>
              <p>
                Only a bounded sample of complaint IDs and text is sent when you
                explicitly generate insights. Do not import real customer PII.
              </p>
            </Panel>
            <Panel
              title="Local intelligence"
              subtitle="Your core workflow works without an API key"
            >
              <dl className="details">
                <div>
                  <dt>Category</dt>
                  <dd>TF-IDF + Logistic Regression</dd>
                </div>
                <div>
                  <dt>Sentiment</dt>
                  <dd>Locally trained Logistic Regression</dd>
                </div>
                <div>
                  <dt>Urgency</dt>
                  <dd>Explainable risk and service rules</dd>
                </div>
                <div>
                  <dt>Grouping mode</dt>
                  <dd>{data.embedding_mode}</dd>
                </div>
                <div>
                  <dt>Embedding method</dt>
                  <dd>{data.embedding_model}</dd>
                </div>
              </dl>
              <p className="notice">
                TF-IDF mode is a lexical fallback, not sentence-transformer
                semantic inference. Enable sentence-transformer mode after
                installing its dependencies and downloading the model.
              </p>
              <p>
                This local portfolio MVP has no authentication. Keep it on your
                machine. Production needs access control, PII handling, backups
                and durable jobs.
              </p>
            </Panel>
          </div>
        )
      )}
    </>
  );
}
