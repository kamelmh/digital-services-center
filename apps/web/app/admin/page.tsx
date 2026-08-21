"use client";
import { useEffect, useState } from "react";
import { listDossiers } from "@/lib/dossiers";
import { Card } from "@/components/ui/button";

export default function AdminPage() {
  const [q, setQ] = useState("");
  const [wilaya, setWilaya] = useState("");
  const [status, setStatus] = useState("");
  const [data, setData] = useState<{ total: number; dossiers: any[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const r = await listDossiers({ q: q || undefined, wilaya: wilaya || undefined, status: status || undefined, limit: 20 });
      setData(r);
    } catch (e: any) {
      setError(String(e.message || e));
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <h1 className="text-2xl font-bold text-navy">Admin — Dossiers (RLS: tenant_id)</h1>
      <p className="text-sm text-gray-600">
        Liste filtrée par <code>tenant_id = anon@local (0000…)</code> — RLS isolée. Search <code>q</code> sur <code>project_name/beneficiary/activity</code>, filtres <code>wilaya/status</code>, pagination <code>limit/offset</code>.
      </p>

      <Card className="mt-6">
        <div className="flex flex-wrap gap-3">
          <input placeholder="Recherche q (nom, bénéficiaire, activité)" value={q} onChange={(e) => setQ(e.target.value)} className="flex-1 min-w-[200px] rounded border px-3 py-2 text-sm" />
          <select value={wilaya} onChange={(e) => setWilaya(e.target.value)} className="rounded border px-3 py-2 text-sm">
            <option value="">Toutes wilayas</option>
            <option value="Oran">Oran</option>
            <option value="Alger">Alger</option>
            <option value="El Bayadh">El Bayadh</option>
          </select>
          <select value={status} onChange={(e) => setStatus(e.target.value)} className="rounded border px-3 py-2 text-sm">
            <option value="">Tous statuts</option>
            <option value="draft">draft</option>
            <option value="queued">queued</option>
            <option value="ready">ready</option>
            <option value="failed">failed</option>
          </select>
          <button onClick={load} className="rounded bg-navy px-4 py-2 text-sm font-semibold text-white">Filtrer</button>
          <a href="/dashboard" className="rounded border px-4 py-2 text-sm">→ Dashboard</a>
        </div>
        {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      </Card>

      <Card className="mt-6">
        <div className="flex justify-between text-sm">
          <span>Total: <b>{data?.total ?? "—"}</b> (tenant_id isolé)</span>
          <span className="text-gray-500">RLS: WHERE tenant_id = anon</span>
        </div>
        <div className="mt-4 overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="py-2">ID</th>
                <th>Projet</th>
                <th>Bénéficiaire</th>
                <th>Wilaya</th>
                <th>Activité</th>
                <th>Coût</th>
                <th>Status</th>
                <th>Tenant</th>
                <th>Créé</th>
              </tr>
            </thead>
            <tbody>
              {(data?.dossiers || []).map((d: any) => (
                <tr key={d.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 font-mono text-xs">{d.id.slice(0, 8)}…</td>
                  <td>{d.project_name}</td>
                  <td>{d.beneficiary_name || "—"}</td>
                  <td>{d.wilaya || "—"}</td>
                  <td>{d.activity_type || "—"}</td>
                  <td>{d.total_cost?.toLocaleString() || "—"}</td>
                  <td>
                    <span className={`rounded px-2 py-1 text-xs ${d.status === "ready" ? "bg-green-100 text-green-700" : "bg-gray-100"}`}>{d.status}</span>
                  </td>
                  <td className="font-mono text-xs">{d.tenant_id.slice(0, 8)}…</td>
                  <td className="text-xs">{d.created_at ? new Date(d.created_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
              {data && data.dossiers.length === 0 && (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-gray-500">
                    Aucun dossier — créez-en un depuis <a href="/dashboard" className="underline">Dashboard</a> (POST /v1/dossiers/feasibility)
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs text-gray-500">
          Vérification RLS: tous les `tenant_id` affichés doivent être identiques (`0000…` pour anon). Un `q=Oran` ne doit pas fuiter les dossiers d&apos;un autre tenant.
        </p>
      </Card>
    </div>
  );
}
