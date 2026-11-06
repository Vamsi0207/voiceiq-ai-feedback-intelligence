import { useEffect, useRef, type ReactNode } from "react";
import { X, AlertCircle, ArrowUpRight, Inbox } from "lucide-react";
import { categories } from "../services/api";
export function Badge({ children }: { children: ReactNode }) {
  return (
    <span
      className={"badge " + String(children).toLowerCase().replaceAll(" ", "-")}
    >
      {children || "Pending"}
    </span>
  );
}
export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="error" role="alert">
      <AlertCircle size={18} />
      {message}
    </div>
  );
}
export function Loading() {
  return (
    <div className="skeleton" aria-label="Loading">
      <div />
      <div />
      <div />
    </div>
  );
}
export function Empty({
  text = "No feedback matches this view.",
}: {
  text?: string;
}) {
  return (
    <div className="empty">
      <Inbox size={36} />
      <h3>Nothing here yet</h3>
      <p>{text}</p>
    </div>
  );
}
export function Heading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}
export function Modal({
  title,
  children,
  onClose,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    dialog.current?.showModal();
    return () => dialog.current?.close();
  }, []);
  return (
    <dialog
      ref={dialog}
      className="modal"
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-heading">
        <h2>{title}</h2>
        <button aria-label="Close details" onClick={onClose}>
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export type FilterValues = {
  category: string;
  sentiment: string;
  urgency: string;
  source: string;
  date_from: string;
  date_to: string;
};
export const initialFilters: FilterValues = {
  category: "",
  sentiment: "",
  urgency: "",
  source: "",
  date_from: "",
  date_to: "",
};
export function Filters({
  value,
  onChange,
  sources = [],
}: {
  value: FilterValues;
  onChange: (v: FilterValues) => void;
  sources?: string[];
}) {
  const update = (key: keyof FilterValues, val: string) =>
    onChange({ ...value, [key]: val });
  return (
    <div className="filters">
      {(
        [
          ["category", "Category", categories],
          ["sentiment", "Sentiment", ["Positive", "Neutral", "Negative"]],
          ["urgency", "Urgency", ["Low", "Medium", "High", "Critical"]],
          ["source", "Source", sources],
        ] as [keyof FilterValues, string, string[]][]
      ).map(([key, label, options]) => (
        <label key={key}>
          <span>{label}</span>
          <select
            aria-label={label}
            value={value[key]}
            onChange={(e) => update(key, e.target.value)}
          >
            <option value="">All {label.toLowerCase()}</option>
            {options.map((o) => (
              <option key={o}>{o}</option>
            ))}
          </select>
        </label>
      ))}
      <label>
        <span>From</span>
        <input
          aria-label="From date"
          type="date"
          value={value.date_from}
          onChange={(e) => update("date_from", e.target.value)}
        />
      </label>
      <label>
        <span>To</span>
        <input
          aria-label="To date"
          type="date"
          value={value.date_to}
          onChange={(e) => update("date_to", e.target.value)}
        />
      </label>
      {Object.values(value).some(Boolean) && (
        <button
          className="text-button"
          onClick={() => onChange(initialFilters)}
        >
          Reset
        </button>
      )}
    </div>
  );
}
export function Panel({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <ArrowUpRight size={17} className="muted" />
      </div>
      {children}
    </section>
  );
}
