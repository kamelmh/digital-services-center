const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Dossier = {
  id: string;
  project_name: string;
  beneficiary_name: string | null;
  wilaya: string | null;
  activity_type: string | null;
  total_cost: number | null;
  status: string;
  pdf_r2_key: string | null;
  created_at: string | null;
  tenant_id: string;
};

export async function listDossiers(params: { q?: string; wilaya?: string; status?: string; limit?: number; offset?: number } = {}) {
  const usp = new URLSearchParams();
  if (params.q) usp.set("q", params.q);
  if (params.wilaya) usp.set("wilaya", params.wilaya);
  if (params.status) usp.set("status", params.status);
  if (params.limit) usp.set("limit", String(params.limit));
  if (params.offset) usp.set("offset", String(params.offset));
  const r = await fetch(`${API}/v1/dossiers?${usp.toString()}`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ total: number; limit: number; offset: number; dossiers: Dossier[] }>;
}

export async function getDossier(id: string) {
  const r = await fetch(`${API}/v1/dossiers/${id}`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
