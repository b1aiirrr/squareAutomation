"use client";

export function StatusPulse({ status }: { status: "running" | "initializing" | "offline" | "posting" | string }) {
  let color = "bg-slate-500";
  let pulse = "animate-none";

  if (status === "running" || status === "posting") {
    color = "bg-emerald-500";
    pulse = "animate-pulse";
  } else if (status === "initializing") {
    color = "bg-yellow-500";
    pulse = "animate-pulse";
  } else if (status === "offline") {
    color = "bg-red-500";
  }

  return (
    <div className="flex shrink-0 items-center justify-center p-1">
      <div className={`h-3 w-3 rounded-full ${color} ${pulse} shadow-[0_0_8px_rgba(0,0,0,0.5)]`} />
    </div>
  );
}
