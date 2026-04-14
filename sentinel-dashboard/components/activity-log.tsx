"use client";

import { useEffect, useMemo, useState } from "react";

import { LogEntry } from "@/lib/types";

type Props = {
  apiBase: string;
  fallbackLogs: LogEntry[];
};

export function ActivityLog({ apiBase, fallbackLogs }: Props) {
  const [events, setEvents] = useState<LogEntry[]>(fallbackLogs ?? []);

  useEffect(() => {
    const stream = new EventSource(`${apiBase}/events`);

    stream.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "keepalive") return;
        setEvents((prev) => [...prev.slice(-249), payload]);
      } catch {
        // ignore malformed events
      }
    };

    stream.onerror = () => {
      stream.close();
    };

    return () => stream.close();
  }, [apiBase]);

  const rendered = useMemo(() => (events.length ? events : fallbackLogs), [events, fallbackLogs]);

  return (
    <article className="rounded-2xl border border-cyan-500/20 bg-panel p-6 shadow-neon">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-cyan-100">Activity Log</h2>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Live SSE</p>
      </div>
      <div className="h-[420px] overflow-auto rounded-xl border border-slate-800 bg-slate-950/70 p-4 font-mono text-xs">
        {rendered.slice().reverse().map((item, idx) => (
          <p key={`${item.ts}-${idx}`} className="mb-2 text-slate-300">
            <span className="text-cyan-400">[{new Date(item.ts).toLocaleTimeString()}]</span>{" "}
            <span className="uppercase text-slate-500">{item.level}</span> {item.message}
          </p>
        ))}
        {!rendered.length && <p className="text-slate-500">No activity yet...</p>}
      </div>
    </article>
  );
}
