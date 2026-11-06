import { useEffect, useRef, useState } from "react";
import {
  UploadCloud,
  FileText,
  Download,
  Play,
  CheckCircle2,
} from "lucide-react";
import { api } from "../services/api";
import { Heading, Panel, ErrorBox } from "../components/UI";
import type { Batch, Job } from "../types";
export function Upload({
  onChange,
  notify,
}: {
  onChange: () => void;
  notify: (s: string) => void;
}) {
  const [file, setFile] = useState<File>(),
    [result, setResult] = useState<Batch>(),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [job, setJob] = useState<Job>();
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return;
    let alive = true;
    const timer = setInterval(
      () =>
        api<Job>("/jobs/" + job.id)
          .then((j) => {
            if (!alive) return;
            setJob(j);
            if (j.status === "completed") {
              onChange();
              notify("Analysis complete. Your feedback is ready to explore.");
            }
            if (j.status === "failed") setError(j.error || "Analysis failed");
          })
          .catch((e) => {
            if (alive) setError(e.message);
          }),
      1200,
    );
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [job, onChange, notify]);
  async function upload() {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);
      const r = await api<Batch>("/complaints/upload", {
        method: "POST",
        body: form,
      });
      setResult(r);
      onChange();
      notify(`Imported ${r.successful_records} records`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function analyze() {
    setError("");
    setBusy(true);
    try {
      setJob(await api<Job>("/complaints/analyze", { method: "POST" }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const running = !!job && ["queued", "running"].includes(job.status);
  return (
    <>
      <Heading
        eyebrow="MAKE EVERY VOICE COUNT"
        title="Upload data"
        description="Bring customer feedback together. We’ll take care of the analysis."
      />
      {error && <ErrorBox message={error} />}
      <div className="upload-grid">
        <Panel
          title="Import customer feedback"
          subtitle="UTF-8 CSV · up to 5 MB and 10,000 rows"
        >
          <div
            className="dropzone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              setFile(e.dataTransfer.files[0]);
            }}
          >
            <span className="upload-icon">
              <UploadCloud size={32} />
            </span>
            <h3>{file ? file.name : "Drop your CSV file here"}</h3>
            <p>or select a file from your computer</p>
            <input
              ref={input}
              type="file"
              accept=".csv,text/csv"
              aria-label="Choose CSV file"
              onChange={(e) => setFile(e.target.files?.[0])}
            />
          </div>
          <button
            className="button primary full"
            disabled={!file || busy || running}
            onClick={upload}
          >
            <UploadCloud size={17} />
            {busy ? "Working…" : "Import feedback"}
          </button>
          <a className="download" href="/api/complaints/example" download>
            <Download size={16} />
            Download example CSV
          </a>
        </Panel>
        <Panel
          title="A clean start for better insights"
          subtitle="A simple, transparent import process"
        >
          <ol className="steps">
            <li>
              <span>1</span>
              <div>
                <h3>Prepare your feedback</h3>
                <p>
                  Required: complaint_id, complaint_text, created_at (ISO date).
                  Optional: customer_id, source, category. Supplied labels are
                  not used as model predictions.
                </p>
              </div>
            </li>
            <li>
              <span>2</span>
              <div>
                <h3>Review the import</h3>
                <p>
                  Duplicate IDs are skipped. Invalid rows include a reason so
                  you can correct and retry.
                </p>
              </div>
            </li>
            <li>
              <span>3</span>
              <div>
                <h3>Analyze and explore</h3>
                <p>
                  Run the local ML pipeline to classify, score urgency and group
                  related complaints.
                </p>
              </div>
            </li>
          </ol>
          <button
            className="button"
            disabled={busy || running}
            onClick={analyze}
          >
            <Play size={16} />
            {running ? "Analysis in progress…" : "Analyze pending feedback"}
          </button>
          {job && (
            <div className="job-status" role="status">
              <strong>{job.status}</strong>
              <span>
                {job.completed} / {job.total} records
              </span>
              <progress max={Math.max(1, job.total)} value={job.completed} />
              {job.status === "completed" && <CheckCircle2 size={18} />}
            </div>
          )}
        </Panel>
      </div>
      {result && (
        <Panel title="Import report" subtitle="Every record is accounted for">
          <div className="import-stats">
            {[
              ["Total rows", result.total_records],
              ["Imported", result.successful_records],
              ["Duplicates", result.duplicate_records],
              ["Invalid", result.failed_records],
            ].map(([k, v]) => (
              <div key={k}>
                <FileText size={18} />
                <strong>{v}</strong>
                <span>{k}</span>
              </div>
            ))}
          </div>
          {result.errors.length > 0 && (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>CSV row</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {result.errors.map((e) => (
                    <tr key={e.row}>
                      <td>{e.row}</td>
                      <td>{e.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      )}
    </>
  );
}
