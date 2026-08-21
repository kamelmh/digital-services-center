"use client";
import { useEffect, useState } from "react";
import { pollJob } from "@/lib/api";

export function JobPollBar({ jobId, onDone }: { jobId: string; onDone: (j: any) => void }) {
  const [job, setJob] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    pollJob(jobId, setJob).then(onDone).catch((e) => setError(String(e)));
  }, [jobId, onDone]);

  if (error) return <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>;
  if (!job) return <div className="text-sm text-gray-500">Queued…</div>;
  return (
    <div className="rounded border p-4">
      <div className="flex justify-between text-sm">
        <span>{job.status} — {job.provider || "…"}</span>
        <span>{job.progress}%</span>
      </div>
      <div className="mt-2 h-2 rounded bg-gray-100">
        <div className="h-2 rounded bg-gold transition-all" style={{ width: `${job.progress}%` }} />
      </div>
      <p className="mt-2 text-xs text-gray-500">Polling GET /v1/dossiers/jobs/{jobId} every 2s — RQ dsc-queue (or inline fallback if Redis absent)</p>
    </div>
  );
}
