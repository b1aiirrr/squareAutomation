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
  rewards: {
    yield_sweep: null,
    launchpools: [],
    referral_ctas: 0,
    daily_claims: {}
  }
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

  const rewards = status.rewards || {};
  const launchpools = rewards.launchpools || [];
  const yieldData = rewards.yield_sweep;

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 p-6 md:p-10">
      {/* Header */}
      <header className="mx-auto mb-8 max-w-7xl">
        <h1 className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-4xl font-bold text-transparent md:text-5xl">
          Sentinel Square
        </h1>
        <p className="mt-2 text-slate-400">Autonomous Content & Rewards Engine v5.0</p>
      </header>

      {/* Core Engine Status */}
      <section className="mx-auto grid max-w-7xl gap-6 md:grid-cols-4">
        <article className="rounded-2xl border border-cyan-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300/80">Engine Status</p>
          <div className="mt-5 flex items-center justify-between">
            <StatusPulse status={status.status} />
            <span className="rounded-full border border-cyan-400/30 px-4 py-1 text-sm text-cyan-200">
              {status.status}
            </span>
          </div>
        </article>

        <article className="rounded-2xl border border-cyan-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300/80">Next Post</p>
          <p className="mt-5 font-mono text-3xl text-cyan-200">{countdown}</p>
          <p className="mt-3 text-xs text-slate-500">Human jitter + sleep windows</p>
        </article>

        <article className="rounded-2xl border border-emerald-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
          <p className="text-xs uppercase tracking-[0.25em] text-emerald-300/80">Posts Today</p>
          <p className="mt-5 text-4xl font-bold text-emerald-200">{status.posts_today}</p>
          <div className="mt-3 h-2 w-full rounded-full bg-slate-800">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all"
              style={{ width: `${Math.min((status.posts_today / 40) * 100, 100)}%` }}
            />
          </div>
          <p className="mt-2 text-xs text-slate-500">Target: 40/day</p>
        </article>

        <article className="rounded-2xl border border-violet-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
          <p className="text-xs uppercase tracking-[0.25em] text-violet-300/80">Total Posts</p>
          <p className="mt-5 text-4xl font-bold text-violet-200">{status.history_size}</p>
          <p className="mt-3 text-xs text-slate-500">All-time historical record</p>
        </article>
      </section>

      {/* Rewards Section */}
      <section className="mx-auto mt-6 max-w-7xl">
        <h2 className="mb-4 text-2xl font-bold text-white">Rewards Hub</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {/* Yield Engine */}
          <article className="rounded-2xl border border-yellow-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500/20 text-xl">💰</div>
              <div>
                <p className="text-sm font-semibold text-yellow-200">Yield Engine</p>
                <p className="text-xs text-slate-400">Simple Earn Sweep</p>
              </div>
            </div>
            <div className="mt-4">
              {yieldData ? (
                <>
                  <p className="text-2xl font-bold text-white">${(yieldData.amount_usdt || 0).toFixed(2)}</p>
                  <p className="text-sm text-yellow-300">APR: {yieldData.apr || 0}%</p>
                  <p className="mt-2 text-xs text-slate-500">
                    Last sweep: {new Date(yieldData.timestamp || Date.now()).toLocaleTimeString()}
                  </p>
                </>
              ) : (
                <p className="text-slate-400">Checking idle balance...</p>
              )}
            </div>
          </article>

          {/* Launchpools */}
          <article className="rounded-2xl border border-blue-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/20 text-xl">🚀</div>
              <div>
                <p className="text-sm font-semibold text-blue-200">Launchpools</p>
                <p className="text-xs text-slate-400">Active Staking Opportunities</p>
              </div>
            </div>
            <div className="mt-4 space-y-2">
              {launchpools.length > 0 ? (
                launchpools.slice(0, 3).map((pool: any, i: number) => (
                  <div key={i} className="flex items-center justify-between rounded-lg bg-slate-800/50 p-2">
                    <span className="text-sm text-blue-200">{pool.token || pool.pool_name}</span>
                    <span className="rounded-full bg-blue-500/20 px-2 py-0.5 text-xs text-blue-300">
                      {pool.apr}% APR
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-slate-400">Scanning for pools...</p>
              )}
            </div>
          </article>

          {/* Referrals */}
          <article className="rounded-2xl border border-green-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20 text-xl">🔗</div>
              <div>
                <p className="text-sm font-semibold text-green-200">Referral CTAs</p>
                <p className="text-xs text-slate-400">Engagement Tracking</p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-slate-800/50 p-3 text-center">
                <p className="text-2xl font-bold text-green-200">{rewards.referral_ctas || 0}</p>
                <p className="text-xs text-slate-400">CTAs Shown</p>
              </div>
              <div className="rounded-lg bg-slate-800/50 p-3 text-center">
                <p className="text-2xl font-bold text-green-200">~{(rewards.referral_ctas || 0) * 0.02}</p>
                <p className="text-xs text-slate-400">Est. Conversions</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      {/* Multi-Account Status */}
      <section className="mx-auto mt-6 max-w-7xl">
        <h2 className="mb-4 text-2xl font-bold text-white">Multi-Account Sync</h2>
        <div className="grid gap-6 md:grid-cols-2">
          <article className="rounded-2xl border border-cyan-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-200">👤</div>
              <div>
                <p className="text-sm font-semibold text-cyan-200">Primary Account</p>
                <p className="text-xs text-slate-400">Trading + Posting</p>
              </div>
              <span className="ml-auto rounded-full bg-emerald-500/20 px-3 py-1 text-xs text-emerald-300">Active</span>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-3">
              <div className="rounded-lg bg-slate-800/50 p-2 text-center">
                <p className="text-lg font-bold text-cyan-200">Spot</p>
                <p className="text-xs text-slate-400">Trading</p>
              </div>
              <div className="rounded-lg bg-slate-800/50 p-2 text-center">
                <p className="text-lg font-bold text-cyan-200">Earn</p>
                <p className="text-xs text-slate-400">Yield</p>
              </div>
              <div className="rounded-lg bg-slate-800/50 p-2 text-center">
                <p className="text-lg font-bold text-cyan-200">Square</p>
                <p className="text-xs text-slate-400">Posts</p>
              </div>
            </div>
          </article>

          <article className="rounded-2xl border border-pink-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-pink-500/20 text-pink-200">👥</div>
              <div>
                <p className="text-sm font-semibold text-pink-200">Friend Account</p>
                <p className="text-xs text-slate-400">Cross-Posting Only</p>
              </div>
              <span className="ml-auto rounded-full bg-emerald-500/20 px-3 py-1 text-xs text-emerald-300">Synced</span>
            </div>
            <div className="mt-4">
              <p className="text-sm text-slate-400">Ramilla Kitar</p>
              <div className="mt-2 flex items-center gap-2">
                <div className="h-2 flex-1 rounded-full bg-slate-800">
                  <div className="h-2 w-1/2 rounded-full bg-gradient-to-r from-pink-500 to-cyan-500" />
                </div>
                <span className="text-xs text-slate-500">50% synced</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      {/* Trading Status */}
      <section className="mx-auto mt-6 max-w-7xl">
        <h2 className="mb-4 text-2xl font-bold text-white">Trading Engine</h2>
        <div className="grid gap-6 md:grid-cols-4">
          <article className="rounded-2xl border border-orange-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <p className="text-xs uppercase tracking-[0.25em] text-orange-300/80">Position Size</p>
            <p className="mt-3 text-3xl font-bold text-orange-200">1%</p>
            <p className="text-xs text-slate-500">of USDT wallet</p>
          </article>
          <article className="rounded-2xl border border-red-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <p className="text-xs uppercase tracking-[0.25em] text-red-300/80">Stop Loss</p>
            <p className="mt-3 text-3xl font-bold text-red-200">-2%</p>
            <p className="text-xs text-slate-500">Hard exit floor</p>
          </article>
          <article className="rounded-2xl border border-green-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-xl">
            <p className="text-xs uppercase tracking-[0.25em] text-green-300/80">Take Profit</p>
            <p className="mt-3 text-3xl font-bold text-green-200">+5%</p>
            <p className="text-xs text-slate-500">Profit target</p>
          </article>
          <article className="rounded-2xl border border-cyan-500/20 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300/80">Mode</p>
            <p className="mt-3 text-3xl font-bold text-cyan-200">Spot</p>
            <p className="text-xs text-slate-500">Market orders only</p>
          </article>
        </div>
      </section>

      {/* Activity Log */}
      <section className="mx-auto mt-6 max-w-7xl">
        <ActivityLog apiBase={API_BASE} fallbackLogs={status.recent_logs} />
      </section>
    </main>
  );
}
