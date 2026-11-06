import { useState } from "react";
import { Link } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts";
import {
  MessageSquare,
  TrendingDown,
  ShieldAlert,
  Layers,
  ArrowUpRight,
  Upload,
} from "lucide-react";
import { useApi } from "../hooks/useApi";
import { query } from "../services/api";
import {
  Heading,
  Filters,
  initialFilters,
  Panel,
  Loading,
  ErrorBox,
  Empty,
} from "../components/UI";
import type { Overview } from "../types";
const colors = [
  "#3973e8",
  "#f08467",
  "#26aa92",
  "#a38bdb",
  "#e7b850",
  "#78a8bd",
  "#cf85ac",
  "#8a9bad",
];
const series = (obj: Record<string, number>) =>
  Object.entries(obj).map(([name, count]) => ({ name, count }));
export function Dashboard({ revision }: { revision: number }) {
  const [filters, setFilters] = useState(initialFilters);
  const params = query(filters);
  const {
    data: d,
    error,
    loading,
  } = useApi<Overview>("/dashboard/overview" + params, revision);
  const trend = useApi<{ date: string; count: number }[]>(
    "/dashboard/trends" + params,
    revision,
  );
  return (
    <>
      <Heading
        eyebrow="YOUR CUSTOMERS, UNDERSTOOD"
        title="Feedback overview"
        description="Turn every customer conversation into a clearer next step."
        action={
          <Link className="button primary" to="/upload">
            <Upload size={16} />
            Import feedback
          </Link>
        }
      />
      <Filters value={filters} onChange={setFilters} sources={d?.sources} />
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorBox message={error} />
      ) : (
        d && (
          <>
            {d.pending > 0 && (
              <p className="notice">
                {d.pending.toLocaleString()} records await analysis. Open Upload
                Data to process them.
              </p>
            )}
            <div className="kpis">
              {[
                {
                  label: "Total feedback",
                  value: d.total.toLocaleString(),
                  note: "Across selected feedback",
                  icon: MessageSquare,
                },
                {
                  label: "Negative sentiment",
                  value: d.negative_percentage + "%",
                  note: "Share of selected feedback",
                  icon: TrendingDown,
                },
                {
                  label: "Needs attention",
                  value: d.elevated_urgency.toLocaleString(),
                  note: "High + critical urgency",
                  icon: ShieldAlert,
                },
                {
                  label: "Recurring issues",
                  value: d.recurring_clusters.toLocaleString(),
                  note: "Groups with 3+ records",
                  icon: Layers,
                },
              ].map(({ label, value, note, icon: Icon }) => (
                <div className="kpi" key={label}>
                  <div className="kpi-label">
                    {label}
                    <span>
                      <Icon size={17} />
                    </span>
                  </div>
                  <strong>{value}</strong>
                  <small>{note}</small>
                </div>
              ))}
            </div>
            <div className="context-strip">
              <span className="live-dot" />
              Leading topic <strong>{d.largest_category}</strong>
              <span>Calculated from your selected feedback</span>
            </div>
            {!d.total ? (
              <Empty text="Import the example CSV or run the seed script to begin." />
            ) : (
              <>
                <div className="chart-grid">
                  <Panel
                    title="Where customers need help"
                    subtitle="Feedback by predicted category"
                  >
                    <ResponsiveContainer width="100%" height={280}>
                      <BarChart
                        data={series(d.categories)}
                        layout="vertical"
                        margin={{ left: 5, right: 25 }}
                      >
                        <CartesianGrid horizontal={false} stroke="#edf0f5" />
                        <XAxis
                          type="number"
                          axisLine={false}
                          tickLine={false}
                        />
                        <YAxis
                          type="category"
                          dataKey="name"
                          width={125}
                          tick={{ fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <Tooltip />
                        <Bar
                          isAnimationActive={false}
                          dataKey="count"
                          fill="#3973e8"
                          radius={[0, 5, 5, 0]}
                          barSize={16}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </Panel>
                  <Panel
                    title="The customer mood"
                    subtitle="Sentiment across selected feedback"
                  >
                    <ResponsiveContainer width="100%" height={230}>
                      <PieChart>
                        <Pie
                          isAnimationActive={false}
                          data={series(d.sentiments)}
                          dataKey="count"
                          nameKey="name"
                          innerRadius={65}
                          outerRadius={94}
                          paddingAngle={4}
                        >
                          {series(d.sentiments).map((x, i) => (
                            <Cell
                              key={x.name}
                              fill={
                                x.name === "Negative"
                                  ? "#f08467"
                                  : x.name === "Positive"
                                    ? "#26aa92"
                                    : colors[i]
                              }
                            />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="legend">
                      {series(d.sentiments).map((s) => (
                        <span key={s.name}>
                          {s.name}
                          <strong>{s.count.toLocaleString()}</strong>
                        </span>
                      ))}
                    </div>
                  </Panel>
                </div>
                <div className="chart-grid">
                  <Panel
                    title="Feedback over time"
                    subtitle="Daily volume · UTC"
                  >
                    {trend.error ? (
                      <ErrorBox message={trend.error} />
                    ) : (
                      <ResponsiveContainer width="100%" height={230}>
                        <LineChart data={trend.data}>
                          <CartesianGrid vertical={false} stroke="#edf0f5" />
                          <XAxis
                            dataKey="date"
                            tickFormatter={(v) => String(v).slice(5)}
                            minTickGap={30}
                            tick={{ fontSize: 11 }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <YAxis axisLine={false} tickLine={false} width={32} />
                          <Tooltip />
                          <Line
                            isAnimationActive={false}
                            type="monotone"
                            dataKey="count"
                            stroke="#3973e8"
                            strokeWidth={2}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    )}
                  </Panel>
                  <Panel
                    title="Urgency breakdown"
                    subtitle="Explainable rules, independent of sentiment"
                  >
                    <ResponsiveContainer width="100%" height={230}>
                      <BarChart
                        data={["Low", "Medium", "High", "Critical"].map(
                          (name) => ({ name, count: d.urgencies[name] || 0 }),
                        )}
                      >
                        <CartesianGrid vertical={false} stroke="#edf0f5" />
                        <XAxis
                          dataKey="name"
                          axisLine={false}
                          tickLine={false}
                        />
                        <YAxis axisLine={false} tickLine={false} width={32} />
                        <Tooltip />
                        <Bar
                          isAnimationActive={false}
                          dataKey="count"
                          radius={[5, 5, 0, 0]}
                        >
                          {["#26aa92", "#e7b850", "#f08467", "#bd536c"].map(
                            (c) => (
                              <Cell key={c} fill={c} />
                            ),
                          )}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </Panel>
                </div>
                <Panel
                  title="Recurring signals"
                  subtitle="Explore the evidence behind the most frequent issues"
                >
                  <div className="ranked-list">
                    {d.clusters.map((c, i) => (
                      <Link to={"/clusters?open=" + c.id} key={c.id}>
                        <span className="rank">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <span className="rank-title">
                          {c.label}
                          <span
                            className="rank-bar"
                            style={{
                              width:
                                Math.max(5, (c.count / d.total) * 100) + "%",
                            }}
                          />
                        </span>
                        <strong>{c.count}</strong>
                        <ArrowUpRight size={16} />
                      </Link>
                    ))}
                  </div>
                  {!d.clusters.length && (
                    <Empty text="Run analysis to discover recurring issues." />
                  )}
                </Panel>
              </>
            )}
          </>
        )
      )}
    </>
  );
}
