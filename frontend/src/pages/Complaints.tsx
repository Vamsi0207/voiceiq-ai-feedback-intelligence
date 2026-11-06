import { useState } from "react";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";
import { useApi } from "../hooks/useApi";
import { query } from "../services/api";
import {
  Heading,
  Filters,
  initialFilters,
  Badge,
  Loading,
  ErrorBox,
  Empty,
} from "../components/UI";
import { ComplaintDetail } from "../components/ComplaintDetail";
import type { Page, Overview } from "../types";
export function Complaints({ revision }: { revision: number }) {
  const [filters, setFilters] = useState(initialFilters),
    [search, setSearch] = useState(""),
    [page, setPage] = useState(1),
    [sort, setSort] = useState("created_at"),
    [direction, setDirection] = useState("desc"),
    [selected, setSelected] = useState<number>();
  const { data, error, loading } = useApi<Page>(
    "/complaints" +
      query({ ...filters, q: search, page, page_size: 15, sort, direction }),
    revision,
  );
  const overview = useApi<Overview>("/dashboard/overview", revision);
  return (
    <>
      <Heading
        eyebrow="THE VOICE BEHIND THE NUMBERS"
        title="Complaint explorer"
        description="Search, investigate, and trace every customer experience."
      />
      <Filters
        value={filters}
        onChange={(v) => {
          setFilters(v);
          setPage(1);
        }}
        sources={overview.data?.sources}
      />
      <div className="toolbar">
        <label className="search">
          <Search size={17} />
          <input
            aria-label="Search complaints"
            placeholder="Search feedback or complaint ID…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </label>
        <select
          aria-label="Sort complaints"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="created_at">Received date</option>
          <option value="urgency">Urgency</option>
          <option value="confidence">Confidence</option>
        </select>
        <select
          aria-label="Sort direction"
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : (
        data && (
          <section className="panel table-panel">
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Customer feedback</th>
                    <th>Category</th>
                    <th>Sentiment</th>
                    <th>Urgency</th>
                    <th>Received</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((c) => (
                    <tr key={c.id}>
                      <td>
                        <button
                          className="complaint-link"
                          onClick={() => setSelected(c.id)}
                        >
                          <small>
                            {c.complaint_id} · {c.source}
                          </small>
                          <span>{c.complaint_text}</span>
                        </button>
                      </td>
                      <td>
                        <span className="category-text">
                          {c.category || "Pending"}
                        </span>
                      </td>
                      <td>
                        <Badge>{c.sentiment}</Badge>
                      </td>
                      <td>
                        <Badge>{c.urgency}</Badge>
                      </td>
                      <td className="nowrap">{c.created_at.slice(0, 10)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!data.items.length && <Empty />}
            <div className="pagination">
              <span>
                {data.total.toLocaleString()} records · Page {page} of{" "}
                {Math.max(1, Math.ceil(data.total / 15))}
              </span>
              <div>
                <button
                  aria-label="Previous page"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  <ChevronLeft size={18} />
                </button>
                <button
                  aria-label="Next page"
                  disabled={page * 15 >= data.total}
                  onClick={() => setPage(page + 1)}
                >
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          </section>
        )
      )}
      {selected && (
        <ComplaintDetail id={selected} onClose={() => setSelected(undefined)} />
      )}
    </>
  );
}
