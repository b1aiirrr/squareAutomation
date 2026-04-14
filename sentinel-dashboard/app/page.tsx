"use client";

import { useEffect, useMemo, useState } from "react";

import { ActivityLog } from "@/components/activity-log";
import { StatusPulse } from "@/components/status-pulse";
import { WorkerStatus } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_WORKER_URL ?? "http://localhost:8585";

const initialStatus: WorkerStatus = {
  status: "offline",
  next_post_at: null,
  last_post_at: null,
  posts_today: 0,
  history_size: 0,
  recent_logs: [],
};

export default function Home() {
  const [status, setStatus] = useState<WorkerStatus>(initialStatus);
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/status`, { cache: "no-store" });
        const data = await response.json();
        setStatus(data);
      } catch {
        setStatus((prev) => ({ ...prev, status: "offline" }));
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 8000);
    return () => clearInterval(interval);
  }, []);

  const countdown = useMemo(() => {
    if (!status.next_post_at) return "--:--:--";
    const distance = new Date(status.next_post_at).getTime() - now;
    if (distance <= 0) return "imminent";
    const hours = Math.floor(distance / 3_600_000);
    const minutes = Math.floor((distance % 3_600_000) / 60_000);
    const seconds = Math.floor((distance % 60_000) / 1000);
    return [hours, minutes, seconds].map((v) => String(v).padStart(2, "0")).join(":");
  }, [status.next_post_at, now]);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-bg to-slate-900 p-6 md:p-10">
      <section className="mx-auto grid max-w-7xl gap-6 md:grid-cols-3">
        <article className="rounded-2xl border border-cyan-500/20 bg-panel p-6 shadow-neon">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300/80">Engine Status</p>
          <div className="mt-5 flex items-center justify-between">
            <StatusPulse status={status.status} />
            <span className="rounded-full border border-cyan-400/30 px-4 py-1 text-sm text-cyan-200">
              {status.status}
            </span>
          </div>
        </article>

        <article className="rounded-2xl border border-cyan-500/20 bg-panel p-6 shadow-neon">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300/80">Next Post Countdown</p>
          <p className="mt-5 font-mono text-4xl text-cyan-200">{countdown}</p>
          <p className="mt-3 text-sm text-slate-400">Target cadence uses randomized jitter and sleep windows.</p>
        </article>

        <article className="rounded-2xl border border-cyan-500/20 bg-panel p-6 shadow-neon">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300/80">Output Metrics</p>
          <div className="mt-5 grid gap-3">
            <div className="rounded-lg border border-slate-700/80 p-3">
              <p className="text-xs text-slate-400">Posts Today</p>
              <p className="text-xl font-semibold text-cyan-100">{status.posts_today}</p>
            </div>
            <div className="rounded-lg border border-slate-700/80 p-3">
              <p className="text-xs text-slate-400">Historical Posts</p>
              <p className="text-xl font-semibold text-cyan-100">{status.history_size}</p>
            </div>
          </div>
        </article>
      </section>

      <section className="mx-auto mt-6 max-w-7xl">
        <ActivityLog apiBase={API_BASE} fallbackLogs={status.recent_logs} />
      </section>
    </main>
  );
}
