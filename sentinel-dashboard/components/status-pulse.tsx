type Props = {
  status: "posting" | "sleeping" | "offline" | string;
};

const palette = {
  posting: "bg-success",
  sleeping: "bg-warning",
  offline: "bg-danger",
};

export function StatusPulse({ status }: Props) {
  const cls = palette[status as keyof typeof palette] ?? "bg-danger";

  return (
    <div className="flex items-center gap-3">
      <span className={`inline-flex h-3 w-3 animate-pulse rounded-full ${cls}`} />
      <span className="text-sm text-slate-300">Live runtime monitor</span>
    </div>
  );
}
