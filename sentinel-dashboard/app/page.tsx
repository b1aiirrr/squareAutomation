"use client";

import { useEffect, useMemo, useState } from "react";

import { ActivityLog } from "@/components/activity-log";
import { StatusPulse } from "@/components/status-pulse";
import { WorkerStatus } from "@/lib/types";

const API_BASE = "/api-worker/api";

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
    <main className="min-h-screen text-slate-100 pb-20">
      {/* Premium Minimal Topbar */}
      <nav className="sticky top-0 z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <div className="relative group">
              <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 opacity-50 blur transition duration-1000 group-hover:opacity-100 group-hover:duration-200" />
              <img src="/logo.png" alt="Logo" className="relative h-10 w-10 rounded-full border border-white/10" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">Sentinel <span className="text-cyan-400">Square</span></h1>
              <div className="flex items-center gap-2">
                <StatusPulse status={status.status} />
                <span className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">{status.status}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-8">
             <div className="hidden md:block text-right">
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Current Cycle</p>
                <p className="font-mono text-sm text-cyan-200">Active v5.1</p>
             </div>
             <div className="h-8 w-px bg-white/10" />
             <div className="text-right">
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Uptime</p>
                <p className="text-sm font-semibold text-emerald-400">99.9%</p>
             </div>
          </div>
        </div>
      </nav>

      <div className="mx-auto max-w-7xl px-6 pt-10">
        {/* Core Metrics Grid */}
        <div className="grid gap-6 md:grid-cols-4">
          <article className="glass-card p-6">
             <div className="flex justify-between">
                <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Core Engine</p>
                <span className="text-xl">⚙️</span>
             </div>
             <p className="mt-4 text-3xl font-bold text-white capitalize">{status.status}</p>
             <p className="mt-1 text-xs text-cyan-400">Autopilot Engaged</p>
          </article>

          <article className="glass-card p-6">
             <div className="flex justify-between">
                <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Next Signal</p>
                <span className="text-xl">📡</span>
             </div>
             <p className="mt-4 font-mono text-3xl font-bold text-cyan-200">{countdown}</p>
             <div className="mt-2 text-[10px] text-slate-400 flex gap-2">
                <span className="h-1 flex-1 rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full bg-cyan-500 animate-pulse w-1/3" />
                </span>
             </div>
          </article>

          <article className="glass-card p-6">
             <div className="flex justify-between">
                <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Earning Cycle</p>
                <span className="text-xl">🔥</span>
             </div>
             <p className="mt-4 text-4xl font-bold text-white">{status.posts_today}<span className="text-lg text-slate-500 font-normal">/40</span></p>
             <div className="mt-4 h-1.5 w-full rounded-full bg-slate-800">
                <div 
                  className="h-1.5 rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500 glow-cyan transition-all duration-1000"
                  style={{ width: `${Math.min((status.posts_today / 40) * 100, 100)}%` }}
                />
             </div>
          </article>

          <article className="glass-card p-6">
             <div className="flex justify-between">
                <p className="text-xs font-bold uppercase tracking-widest text-slate-500">Historical Alpha</p>
                <span className="text-xl">📚</span>
             </div>
             <p className="mt-4 text-4xl font-bold text-white">{status.history_size}</p>
             <p className="mt-1 text-xs text-slate-500">Total Valid Submissions</p>
          </article>
        </div>

        {/* Intelligence Split View */}
        <div className="mt-8 grid gap-8 lg:grid-cols-3">
          {/* Main Console */}
          <div className="lg:col-span-2 space-y-8">
            <section className="glass-card overflow-hidden">
              <div className="border-b border-white/5 bg-white/5 px-6 py-4 flex justify-between items-center">
                <h2 className="text-sm font-bold uppercase tracking-widest text-slate-300">Strategy Engine Status</h2>
                <div className="flex gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span className="h-2 w-2 rounded-full bg-emerald-500/30" />
                </div>
              </div>
              <div className="p-6">
                <div className="grid gap-6 md:grid-cols-3">
                  <div className="rounded-xl bg-white/5 p-4 border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Trading Mode</p>
                    <p className="text-lg font-bold text-orange-400">SPOT</p>
                  </div>
                  <div className="rounded-xl bg-white/5 p-4 border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Risk Level</p>
                    <p className="text-lg font-bold text-red-400 font-mono">1.0% MAX</p>
                  </div>
                  <div className="rounded-xl bg-white/5 p-4 border border-white/5">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Yield Status</p>
                    <p className="text-lg font-bold text-emerald-400">ACTIVE</p>
                  </div>
                </div>
              </div>
            </section>

            <ActivityLog apiBase={API_BASE} fallbackLogs={status.recent_logs} />
          </div>

          {/* Right Panels */}
          <div className="space-y-8">
            <section className="glass-card p-6 border-yellow-500/20">
              <div className="flex items-center gap-4 mb-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-yellow-500/20 text-2xl animate-float">💰</div>
                <div>
                  <h3 className="font-bold text-yellow-200">Rewards Vault</h3>
                  <p className="text-xs text-slate-500">Autonomous Compounder</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="rounded-2xl bg-gradient-to-br from-yellow-500/10 to-transparent p-5 border border-yellow-500/10">
                   <p className="text-[10px] uppercase font-bold text-yellow-500/60 mb-1">Simple Earn Sweep</p>
                   {yieldData ? (
                    <>
                      <div className="flex items-baseline gap-1">
                        <span className="text-3xl font-bold text-white">${(yieldData.amount_usdt || 0).toFixed(2)}</span>
                        <span className="text-xs text-emerald-400 font-bold">+{yieldData.apr || 0}% APR</span>
                      </div>
                      <p className="mt-2 text-[10px] text-slate-500">Pulse: {new Date(yieldData.timestamp || Date.now()).toLocaleTimeString()}</p>
                    </>
                   ) : (
                    <p className="text-slate-500 animate-pulse">Scanning wallet...</p>
                   )}
                </div>

                <div className="rounded-2xl bg-white/5 p-5 border border-white/5">
                  <p className="text-[10px] uppercase font-bold text-blue-400/60 mb-2">Launchpool Staking</p>
                  <div className="space-y-2">
                    {launchpools.slice(0, 3).map((pool: any, i: number) => (
                      <div key={i} className="flex items-center justify-between group">
                        <span className="text-sm text-slate-300 group-hover:text-cyan-400 transition-colors uppercase font-mono">{pool.token || pool.pool_name}</span>
                        <span className="text-xs font-bold text-cyan-500">{pool.apr}%</span>
                      </div>
                    ))}
                    {launchpools.length === 0 && <p className="text-xs text-slate-600 italic">No cycles active</p>}
                  </div>
                </div>
              </div>
            </section>

            <section className="glass-card p-6 border-pink-500/20">
              <div className="flex items-center gap-4 mb-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-pink-500/20 text-2xl">👥</div>
                <div>
                  <h3 className="font-bold text-pink-200">Account Sync</h3>
                  <p className="text-xs text-slate-500">Cross-Platform Relay</p>
                </div>
              </div>
              
              <div className="space-y-5">
                 <div className="flex justify-between items-center bg-white/5 rounded-xl p-3 border border-white/5">
                    <span className="text-xs font-semibold text-slate-300">Ramilla Kitar</span>
                    <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-bold">SYNCED</span>
                 </div>
                 <div>
                    <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-2 uppercase">
                       <span>Relay Progress</span>
                       <span className="text-pink-400">50%</span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-slate-800">
                       <div className="h-1.5 rounded-full bg-gradient-to-r from-pink-500 to-cyan-500 w-1/2" />
                    </div>
                 </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
