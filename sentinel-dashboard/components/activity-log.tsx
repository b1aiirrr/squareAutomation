"use client";

import { useEffect, useState } from "react";

interface LogEntry {
  timestamp: string;
  level: "info" | "warning" | "error";
  message: string;
}

export function ActivityLog({ apiBase, fallbackLogs = [] }: { apiBase: string, fallbackLogs?: LogEntry[] }) {
  const [logs, setLogs] = useState<LogEntry[]>(fallbackLogs);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch(`${apiBase}/logs/history?limit=10`);
        const data = await response.json();
        if (data.logs && data.logs.length > 0) {
          setLogs(data.logs);
        }
      } catch (e) {
        console.error("Failed to fetch logs", e);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, [apiBase]);

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
      <h3 className="mb-4 text-xs uppercase tracking-[0.25em] text-slate-400">Live Activity Log</h3>
      <div className="space-y-3 font-mono text-xs text-slate-300 h-64 overflow-y-auto">
        {logs.length > 0 ? logs.map((log, i) => (
          <div key={i} className="flex gap-4 border-b border-slate-800 pb-2">
            <span className="text-slate-500 whitespace-nowrap">
              {new Date(log.timestamp).toLocaleTimeString()}
            </span>
            <span className={`px-2 rounded uppercase font-bold text-[10px] items-center flex ${
              log.level === 'error' ? 'bg-red-900/50 text-red-400' :
              log.level === 'warning' ? 'bg-orange-900/50 text-orange-400' :
              'bg-blue-900/50 text-blue-400'
            }`}>
              {log.level}
            </span>
            <span className="text-slate-200 break-words">{log.message}</span>
          </div>
        )) : (
          <p className="text-slate-500 italic">No recent activity detected.</p>
        )}
      </div>
    </div>
  );
}
