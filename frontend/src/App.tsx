import { useCallback, useEffect, useState } from "react";
import { NavLink, Routes, Route, Link, useLocation } from "react-router-dom";
import {
  AudioLines,
  LayoutDashboard,
  MessageSquare,
  Layers,
  Sparkles,
  ChartNoAxesCombined,
  Upload,
  Settings as SettingsIcon,
  ChevronRight,
  Check,
  Menu,
  X,
} from "lucide-react";
import { Dashboard } from "./pages/Dashboard";
import { Complaints } from "./pages/Complaints";
import { Clusters } from "./pages/Clusters";
import { Insights } from "./pages/Insights";
import { Upload as UploadPage } from "./pages/Upload";
import { Evaluation } from "./pages/Evaluation";
import { Settings } from "./pages/Settings";
import { useApi } from "./hooks/useApi";
import type { AIStatus } from "./types";
const navigation = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/complaints", label: "Complaints", icon: MessageSquare },
  { to: "/clusters", label: "Recurring Issues", icon: Layers },
  { to: "/insights", label: "Product Insights", icon: Sparkles },
  { to: "/evaluation", label: "Model Evaluation", icon: ChartNoAxesCombined },
  { to: "/upload", label: "Upload Data", icon: Upload },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];
export default function App() {
  const [revision, setRevision] = useState(0),
    [toast, setToast] = useState(""),
    [mobile, setMobile] = useState(false);
  const status = useApi<AIStatus>("/settings/ai-status");
  const location = useLocation();
  const change = useCallback(() => setRevision((r) => r + 1), []);
  const notify = useCallback((s: string) => setToast(s), []);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 7000);
    return () => clearTimeout(timer);
  }, [toast]);
  useEffect(() => setMobile(false), [location.pathname]);
  return (
    <div className="app-shell">
      <aside className={"sidebar " + (mobile ? "open" : "")}>
        <Link to="/" className="brand">
          <span>
            <AudioLines size={25} />
          </span>
          Voice<span className="brand-iq">IQ</span>
          <small>INTELLIGENCE PLATFORM</small>
        </Link>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {navigation.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === "/"}>
              <Icon size={18} />
              <span>{label}</span>
              {to === "/insights" && (
                <span className="nav-new" aria-hidden="true">
                  AI
                </span>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-note">
          <span className="live-dot" />
          <strong>Your feedback. Clearer.</strong>
          <p>From customer voices to decisions that matter.</p>
        </div>
        <div className="workspace-user">
          <span>VI</span>
          <div>
            <strong>VoiceIQ workspace</strong>
            <small>Local portfolio edition</small>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div>
            <button
              className="mobile-toggle"
              aria-label="Toggle navigation"
              onClick={() => setMobile(!mobile)}
            >
              <Menu size={22} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>
              {navigation.find((n) => n.to === location.pathname)?.label ||
                "Page"}
            </strong>
          </div>
          <div>
            <Link to="/settings" className="ai-status">
              <span className="live-dot" />
              {status.error
                ? "Service unavailable"
                : status.data?.configured
                  ? "AI configured"
                  : "Local intelligence"}
            </Link>
            <span className="avatar">VI</span>
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard revision={revision} />} />
            <Route
              path="/complaints"
              element={<Complaints revision={revision} />}
            />
            <Route
              path="/clusters"
              element={<Clusters revision={revision} />}
            />
            <Route
              path="/insights"
              element={
                <Insights
                  revision={revision}
                  onChange={change}
                  notify={notify}
                />
              }
            />
            <Route
              path="/upload"
              element={<UploadPage onChange={change} notify={notify} />}
            />
            <Route
              path="/evaluation"
              element={<Evaluation revision={revision} />}
            />
            <Route path="/settings" element={<Settings />} />
            <Route
              path="*"
              element={
                <div className="empty">
                  <h1>Page not found</h1>
                  <Link to="/">Back to dashboard</Link>
                </div>
              }
            />
          </Routes>
          <footer>
            VoiceIQ{" "}
            <span>Customer feedback, translated into product clarity.</span>
            <small>Local MVP · Synthetic demo data</small>
          </footer>
        </main>
      </div>
      {toast && (
        <div className="toast" role="status">
          <Check size={18} />
          <span>{toast}</span>
          <button
            aria-label="Dismiss notification"
            onClick={() => setToast("")}
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
