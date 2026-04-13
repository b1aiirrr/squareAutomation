"use client";

import { useState, useEffect, useRef, useCallback } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface EngineState {
  uptime_start: string;
  posts_today: number;
  posts_total: number;
  last_post: {
    time: string;
    persona: string;
    status: string;
    post_id?: string;
    post_url?: string;
    content_preview?: string;
    error?: string;
  } | null;
  next_post_time: string | null;
  sleep_window: { start: string; end: string };
  is_sleeping: boolean;
  engine_status: string;
}

interface LogEntry {
  timestamp: string;
  event: string;
  persona?: string;
  post_id?: string;
  post_url?: string;
  content_preview?: string;
  error?: string;
  reason?: string;
  posts_today?: number;
  [key: string]: unknown;
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8585";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatUptime(startIso: string): string {
  const start = new Date(startIso).getTime();
  const now = Date.now();
  const diff = Math.max(0, Math.floor((now - start) / 1000));

  const days = Math.floor(diff / 86400);
  const hours = Math.floor((diff % 86400) / 3600);
  const mins = Math.floor((diff % 3600) / 60);
  const secs = diff % 60;

  if (days > 0) return `${days}d ${hours}h ${mins}m`;
  if (hours > 0) return `${hours}h ${mins}m ${secs}s`;
  return `${mins}m ${secs}s`;
}

function getCountdown(targetIso: string | null): {
  hours: string;
  minutes: string;
  seconds: string;
  total: number;
} {
  if (!targetIso) return { hours: "--", minutes: "--", seconds: "--", total: 0 };

  const diff = Math.max(
    0,
    Math.floor((new Date(targetIso).getTime() - Date.now()) / 1000)
  );
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  const s = diff % 60;

  return {
    hours: String(h).padStart(2, "0"),
    minutes: String(m).padStart(2, "0"),
    seconds: String(s).padStart(2, "0"),
    total: diff,
  };
}

function personaBadgeClass(persona: string): string {
  const p = persona.toLowerCase();
  if (p === "technical") return "badge-technical";
  if (p === "news") return "badge-news";
  if (p === "educator") return "badge-educator";
  if (p === "community") return "badge-community";
  return "badge-technical";
}

function eventColor(event: string): string {
  if (event === "published") return "text-[#00c48c]";
  if (event === "publish_failed" || event === "generation_failed")
    return "text-[#ff6b6b]";
  if (event === "skipped") return "text-[#ffab00]";
  if (event === "daily_reset") return "text-[#6c8cff]";
  return "text-[#7b8ba5]";
}

function statusConfig(status: string, isSleeping: boolean) {
  if (isSleeping)
    return {
      label: "SLEEPING",
      color: "#ffab00",
      pulseClass: "pulse-amber",
      bgClass: "bg-[rgba(255,171,0,0.15)]",
    };
  if (status === "running")
    return {
      label: "RUNNING",
      color: "#00c48c",
      pulseClass: "pulse-green",
      bgClass: "bg-[rgba(0,196,140,0.15)]",
    };
  if (status === "stopped" || status === "error")
    return {
      label: status.toUpperCase(),
      color: "#ff6b6b",
      pulseClass: "pulse-red",
      bgClass: "bg-[rgba(255,107,107,0.15)]",
    };
  return {
    label: "INITIALIZING",
    color: "#6c8cff",
    pulseClass: "pulse-green",
    bgClass: "bg-[rgba(108,140,255,0.15)]",
  };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function Dashboard() {
  const [state, setState] = useState<EngineState | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [countdown, setCountdown] = useState(getCountdown(null));
  const [uptimeStr, setUptimeStr] = useState("--");
  const [connected, setConnected] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  // --- Fetch status ---
  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/status`);
      if (res.ok) {
        const data: EngineState = await res.json();
        setState(data);
        setConnected(true);
      }
    } catch {
      setConnected(false);
    }
  }, []);

  // --- SSE log stream ---
  useEffect(() => {
    // Fetch initial log history
    fetch(`${API_URL}/api/logs/history?limit=50`)
      .then((r) => r.json())
      .then((data) => {
        if (data.logs) setLogs(data.logs);
      })
      .catch(() => {});

    // Set up SSE stream
    const eventSource = new EventSource(`${API_URL}/api/logs`);

    eventSource.addEventListener("log", (e) => {
      try {
        const entry: LogEntry = JSON.parse(e.data);
        setLogs((prev) => [...prev.slice(-200), entry]);
      } catch {
        // ignore malformed entries
      }
    });

    eventSource.onerror = () => {
      setConnected(false);
    };

    return () => eventSource.close();
  }, []);

  // --- Poll status every 10s ---
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  // --- Countdown + uptime ticker (every second) ---
  useEffect(() => {
    const tick = setInterval(() => {
      if (state?.next_post_time) {
        setCountdown(getCountdown(state.next_post_time));
      }
      if (state?.uptime_start) {
        setUptimeStr(formatUptime(state.uptime_start));
      }
    }, 1000);
    return () => clearInterval(tick);
  }, [state?.next_post_time, state?.uptime_start]);

  // --- Auto-scroll logs ---
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // --- Status config ---
  const sc = statusConfig(
    state?.engine_status ?? "initializing",
    state?.is_sleeping ?? false
  );

  // --- Persona stats from logs ---
  const personaCounts = logs.reduce(
    (acc, l) => {
      if (l.event === "published" && l.persona) {
        const p = l.persona.toLowerCase();
        acc[p] = (acc[p] || 0) + 1;
      }
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="relative z-10 min-h-screen flex flex-col font-[family-name:var(--font-inter)]">
      {/* ===== HEADER ===== */}
      <header className="px-6 py-5 flex items-center justify-between border-b border-[rgba(255,255,255,0.06)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#f0b90b] to-[#d4a00a] flex items-center justify-center">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#05080f"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-[#e8ecf4]">
              Sentinel-Square
            </h1>
            <p className="text-xs text-[#7b8ba5] -mt-0.5">
              Autonomous Content Engine v4.0
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Connection status */}
          <div className="flex items-center gap-2 text-xs">
            <div
              className={`w-2 h-2 rounded-full ${
                connected ? "bg-[#00c48c]" : "bg-[#ff6b6b]"
              }`}
            />
            <span className="text-[#7b8ba5]">
              {connected ? "CONNECTED" : "DISCONNECTED"}
            </span>
          </div>

          {/* Engine status badge */}
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${sc.bgClass}`}
            style={{ color: sc.color }}
          >
            <div
              className={`w-2 h-2 rounded-full ${sc.pulseClass}`}
              style={{ backgroundColor: sc.color }}
            />
            {sc.label}
          </div>
        </div>
      </header>

      {/* ===== STATS BAR ===== */}
      <div className="px-6 py-4 grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatCard
          label="Uptime"
          value={uptimeStr}
          icon={
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#6c8cff"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
          }
        />
        <StatCard
          label="Posts Today"
          value={`${state?.posts_today ?? 0}`}
          sub={`/ ${40} target`}
          icon={
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#f0b90b"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <path d="M12 20V10" />
              <path d="M18 20V4" />
              <path d="M6 20v-4" />
            </svg>
          }
        />
        <StatCard
          label="Total Posts"
          value={`${state?.posts_total ?? 0}`}
          icon={
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#00c48c"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          }
        />
        <StatCard
          label="Sleep Window"
          value={`${state?.sleep_window?.start ?? "--"} – ${state?.sleep_window?.end ?? "--"}`}
          sub="EAT"
          icon={
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#ffab00"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <path d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z" />
            </svg>
          }
        />
        <StatCard
          label="API Limit"
          value={`${state?.posts_today ?? 0} / 100`}
          sub="daily max"
          icon={
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#a855f7"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0110 0v4" />
            </svg>
          }
        />
      </div>

      {/* ===== MAIN GRID ===== */}
      <div className="flex-1 px-6 pb-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* --- Countdown Panel --- */}
        <div className="glass-card p-6 flex flex-col items-center justify-center lg:col-span-1">
          <p className="text-xs text-[#7b8ba5] uppercase tracking-widest mb-4">
            Next Scheduled Post
          </p>

          <div className="flex items-center gap-3 mb-6">
            <CountdownDigit value={countdown.hours} label="HRS" />
            <span className="text-2xl text-[#4a5568] font-light mt-[-16px]">
              :
            </span>
            <CountdownDigit value={countdown.minutes} label="MIN" />
            <span className="text-2xl text-[#4a5568] font-light mt-[-16px]">
              :
            </span>
            <CountdownDigit value={countdown.seconds} label="SEC" />
          </div>

          {/* Last post info */}
          {state?.last_post && (
            <div className="w-full mt-2 p-3 rounded-xl bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.04)]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-[#7b8ba5]">Last Post</span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${personaBadgeClass(
                    state.last_post.persona
                  )}`}
                >
                  {state.last_post.persona}
                </span>
              </div>
              <p className="text-xs text-[#7b8ba5] leading-relaxed line-clamp-3">
                {state.last_post.content_preview || state.last_post.error || "—"}
              </p>
              {state.last_post.post_url && (
                <a
                  href={state.last_post.post_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-2 text-xs text-[#f0b90b] hover:underline"
                >
                  View on Binance Square →
                </a>
              )}
            </div>
          )}

          {/* Persona distribution */}
          {Object.keys(personaCounts).length > 0 && (
            <div className="w-full mt-4">
              <p className="text-xs text-[#7b8ba5] mb-2">Persona Distribution</p>
              <div className="space-y-1.5">
                {Object.entries(personaCounts).map(([persona, count]) => {
                  const total = Object.values(personaCounts).reduce(
                    (a, b) => a + b,
                    0
                  );
                  const pct = total > 0 ? (count / total) * 100 : 0;
                  return (
                    <div key={persona} className="flex items-center gap-2">
                      <span
                        className={`text-[10px] w-20 px-1.5 py-0.5 rounded text-center ${personaBadgeClass(
                          persona
                        )}`}
                      >
                        {persona}
                      </span>
                      <div className="flex-1 h-1.5 rounded-full bg-[rgba(255,255,255,0.04)] overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{
                            width: `${pct}%`,
                            background:
                              persona === "technical"
                                ? "#6c8cff"
                                : persona === "news"
                                  ? "#f0b90b"
                                  : persona === "educator"
                                    ? "#00c48c"
                                    : "#a855f7",
                          }}
                        />
                      </div>
                      <span className="text-[10px] text-[#7b8ba5] w-8 text-right">
                        {count}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* --- Activity Log --- */}
        <div className="glass-card flex flex-col lg:col-span-2 min-h-[400px]">
          <div className="px-5 py-4 flex items-center justify-between border-b border-[rgba(255,255,255,0.06)]">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#00c48c] pulse-green" />
              <h2 className="text-sm font-medium text-[#e8ecf4]">
                Activity Log
              </h2>
            </div>
            <span className="text-xs text-[#4a5568]">
              {logs.length} entries
            </span>
          </div>

          <div className="flex-1 overflow-y-auto log-stream px-5 py-3 space-y-1 font-[family-name:var(--font-mono)] text-xs">
            {logs.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-[rgba(255,255,255,0.03)] flex items-center justify-center">
                    <svg
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#4a5568"
                      strokeWidth="1.5"
                    >
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                      <path d="M14 2v6h6" />
                      <path d="M16 13H8" />
                      <path d="M16 17H8" />
                    </svg>
                  </div>
                  <p className="text-[#4a5568]">
                    {connected
                      ? "Waiting for first post..."
                      : "Connecting to worker..."}
                  </p>
                </div>
              </div>
            ) : (
              logs.map((log, i) => (
                <div
                  key={`${log.timestamp}-${i}`}
                  className="log-entry flex items-start gap-2 py-1.5 border-b border-[rgba(255,255,255,0.03)] last:border-0"
                >
                  <span className="text-[#4a5568] shrink-0 w-[140px]">
                    {log.timestamp
                      ? new Date(log.timestamp).toLocaleTimeString("en-GB", {
                          hour: "2-digit",
                          minute: "2-digit",
                          second: "2-digit",
                        })
                      : "--:--:--"}
                  </span>
                  <span
                    className={`shrink-0 w-[100px] ${eventColor(log.event)}`}
                  >
                    {log.event}
                  </span>
                  {log.persona && (
                    <span
                      className={`shrink-0 px-1.5 py-0.5 rounded text-[10px] ${personaBadgeClass(
                        log.persona
                      )}`}
                    >
                      {log.persona}
                    </span>
                  )}
                  <span className="text-[#7b8ba5] truncate">
                    {log.content_preview ||
                      log.error ||
                      log.reason ||
                      log.post_url ||
                      ""}
                  </span>
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
        </div>
      </div>

      {/* ===== FOOTER ===== */}
      <footer className="px-6 py-4 border-t border-[rgba(255,255,255,0.06)] flex items-center justify-between text-xs text-[#4a5568]">
        <span>Sentinel-Square v4.0 — Built by Blair Momanyi</span>
        <span>
          Powered by Gemini AI • Binance Square API
        </span>
      </footer>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------
function StatCard({
  label,
  value,
  sub,
  icon,
}: {
  label: string;
  value: string;
  sub?: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="glass-card px-4 py-3 flex items-center gap-3">
      <div className="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.03)] flex items-center justify-center shrink-0">
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-[10px] text-[#7b8ba5] uppercase tracking-wider">
          {label}
        </p>
        <div className="flex items-baseline gap-1.5">
          <p className="text-sm font-semibold text-[#e8ecf4] stat-value truncate">
            {value}
          </p>
          {sub && (
            <span className="text-[10px] text-[#4a5568] shrink-0">{sub}</span>
          )}
        </div>
      </div>
    </div>
  );
}

function CountdownDigit({
  value,
  label,
}: {
  value: string;
  label: string;
}) {
  return (
    <div className="flex flex-col items-center">
      <div className="w-16 h-16 rounded-xl bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.06)] flex items-center justify-center">
        <span
          key={value}
          className="text-3xl font-bold text-[#f0b90b] digit-change font-[family-name:var(--font-mono)]"
        >
          {value}
        </span>
      </div>
      <span className="text-[9px] text-[#4a5568] uppercase tracking-widest mt-1.5">
        {label}
      </span>
    </div>
  );
}
