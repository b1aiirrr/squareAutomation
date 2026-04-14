export type LogEntry = {
  ts: string;
  level: string;
  message: string;
};

export type WorkerStatus = {
  status: string;
  next_post_at: string | null;
  last_post_at: string | null;
  posts_today: number;
  history_size: number;
  recent_logs: LogEntry[];
};
