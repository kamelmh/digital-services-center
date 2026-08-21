const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createFeasibility(body: { business_type: string; location: string; wilaya: string; investment: number }) {
  const res = await fetch(`${API}/v1/dossiers/feasibility`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ job_id: string; status: string }>;
}

export async function getJob(job_id: string) {
  const res = await fetch(`${API}/v1/dossiers/jobs/${job_id}`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ job_id: string; type: string; status: string; progress: number; provider: string; result: any; error: string | null }>;
}

export async function pollJob(job_id: string, onUpdate: (j: any) => void, interval = 2000) {
  let attempts = 0;
  while (attempts < 60) {
    const j = await getJob(job_id);
    onUpdate(j);
    if (j.status === "done" || j.status === "failed") return j;
    await new Promise((r) => setTimeout(r, interval));
    attempts++;
  }
  throw new Error("Poll timeout");
}
