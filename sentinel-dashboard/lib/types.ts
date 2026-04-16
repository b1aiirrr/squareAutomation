export interface WorkerStatus {
  status: "running" | "initializing" | "offline" | "posting" | string;
  next_post_at: string | null;
  last_post_at: string | null;
  posts_today: number;
  history_size: number;
  recent_logs: any[];
  rewards: {
    yield_sweep: any | null;
    launchpools: any[];
    referral_ctas: number;
    daily_claims: Record<string, any>;
  };
}
