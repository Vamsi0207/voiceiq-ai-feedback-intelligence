import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import App from "./App";
const overview = {
  total: 42,
  negative_percentage: 50,
  elevated_urgency: 7,
  largest_category: "UPI & Payments",
  recurring_clusters: 2,
  categories: { "UPI & Payments": 30, Other: 12 },
  sentiments: { Negative: 21, Positive: 21 },
  urgencies: { High: 7, Low: 35 },
  sources: ["Email"],
  clusters: [],
  pending: 0,
};
function mock(handler?: (url: string, options?: RequestInit) => unknown) {
  const fetch = vi.fn(async (input: string, options?: RequestInit) => {
    const url = String(input);
    const custom = handler?.(url, options);
    return {
      ok: true,
      json: async () =>
        custom ??
        (url.includes("ai-status")
          ? { configured: false, provider: "deterministic" }
          : url.includes("overview")
            ? overview
            : url.includes("complaints?")
              ? { items: [], total: 0, page: 1, page_size: 15 }
              : url.includes("executive-summary")
                ? { summary: "Calculated overview" }
                : []),
    } as Response;
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
function mount(path = "/") {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}
describe("VoiceIQ", () => {
  it("renders actual dashboard metrics", async () => {
    mock();
    mount();
    expect(await screen.findByText("42")).toBeInTheDocument();
    expect(screen.getByText("50%")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Feedback overview" }),
    ).toBeInTheDocument();
  });
  it("navigates to settings and explains no-key mode", async () => {
    mock();
    mount();
    await userEvent.click(screen.getByRole("link", { name: "Settings" }));
    expect(
      await screen.findByRole("heading", { name: "Workspace settings" }),
    ).toBeInTheDocument();
    expect(await screen.findByText("No-key mode")).toBeInTheDocument();
  });
  it("shows API errors without fabricated metrics", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue({
          ok: false,
          status: 503,
          json: async () => ({ detail: "Service unavailable" }),
        }),
    );
    mount();
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Service unavailable",
    );
    expect(screen.queryByText("42")).not.toBeInTheDocument();
  });
  it("sends complaint search and filters to the backend", async () => {
    const fetch = mock();
    mount("/complaints");
    await screen.findByRole("table");
    await userEvent.selectOptions(screen.getByLabelText("Urgency"), "Critical");
    await userEvent.type(screen.getByLabelText("Search complaints"), "debit");
    await waitFor(() =>
      expect(
        fetch.mock.calls.some(
          ([u]) =>
            String(u).includes("urgency=Critical") &&
            String(u).includes("q=debit"),
        ),
      ).toBe(true),
    );
  });
  it("uploads multipart CSV and renders invalid row report", async () => {
    const fetch = mock((url) =>
      url.includes("/upload")
        ? {
            total_records: 3,
            successful_records: 1,
            duplicate_records: 1,
            failed_records: 1,
            errors: [{ row: 3, reason: "Bad date" }],
          }
        : undefined,
    );
    mount("/upload");
    const file = new File(
      ["complaint_id,complaint_text,created_at\n1,test,2026-01-01"],
      "example.csv",
      { type: "text/csv" },
    );
    await userEvent.upload(screen.getByLabelText("Choose CSV file"), file);
    await userEvent.click(
      screen.getByRole("button", { name: "Import feedback" }),
    );
    expect(await screen.findByText("Bad date")).toBeInTheDocument();
    expect(fetch.mock.calls.some(([, o]) => o?.body instanceof FormData)).toBe(
      true,
    );
  });
  it("renders insight evidence and priority", async () => {
    mock((url) =>
      url.includes("/insights?")
        ? [
            {
              id: 1,
              title: "Unresolved payment reversals",
              related_category: "UPI & Payments",
              frequency: 15,
              priority: "High",
              urgency: "High",
              priority_score: 82,
              description: "Customers report failed debits.",
              recommendation: "Review reconciliation.",
              success_metric: "Reversal latency",
              supporting_complaint_ids: ["C1"],
              provider: "deterministic",
              model_name: "rules",
              reasoning: "Calculated priority",
            },
          ]
        : undefined,
    );
    mount("/insights");
    expect(
      await screen.findByText("Unresolved payment reversals"),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "C1" })).toBeInTheDocument();
    expect(screen.getByText("82")).toBeInTheDocument();
  });
  it("reset clears dashboard filters", async () => {
    const fetch = mock();
    mount();
    await screen.findByText("42");
    fireEvent.change(screen.getByLabelText("Category"), {
      target: { value: "Loans" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByLabelText("Category")).toHaveValue("");
    expect(fetch).toHaveBeenCalled();
  });
});
