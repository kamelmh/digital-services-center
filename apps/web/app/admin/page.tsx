"use client";
import { useEffect, useState } from "react";
import { listDossiers, getDossier } from "@/lib/dossiers";
import { Card } from "@/components/ui/button";
import { PdfViewer } from "@/components/PdfViewer";
import { Button } from "@/components/ui/button";

export default function AdminPage() {
  const [q, setQ] = useState("");
  const [wilaya, setWilaya] = useState("");
  const [status, setStatus] = useState("");
  const [data, setData] = useState<{ total: number; dossiers: any[] } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loadingExport, setLoadingExport] = useState(false);

  async function load() {
    setError(null);
    try {
      const r = await listDossiers({ q: q || undefined, wilaya: wilaya || undefined, status: status || undefined, limit: 50 });
      setData(r);
      setSelected(new Set());
    } catch (e: any) {
      setError(String(e.message || e));
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleExport() {
    if (selected.size === 0) {
      alert("Sélectionnez au moins un dossier à exporter");
      return;
    }
    setLoadingExport(true);
    try {
      const ids = Array.from(selected);
      const r = await fetch(`${API}/v1/dossiers/export-csv?ids=${ids.join(",")}`, {
        method: "GET",
        headers: { "Accept": "text/csv" },
      });
      if (!r.ok) throw new Error(await r.text());
      const blob = await r.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `dossiers-${Date.now()}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e: any) {
      alert(`Erreur export: ${e.message}`);
    } finally {
      setLoadingExport(false);
    }
  }

  function toggleSelect(id: string) {
    setSelected((s) => {
      const next = new Set(s);
      if (s.has(id)) next.delete(id);else next.add(id);
      return next;
    });
  }

  function isSelected(id: string) {
    return selected.has(id);
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <h1 className="text-2xl font-bold text-navy">Admin — Dossiers (RLS: tenant_id)</h1>
      <p className="text-sm text-gray-600">
        Filtre <code>q</code> sur <code>project_name/beneficiary/activity</code>, <code>wilaya</code>, <code>status</code>. RLS: `WHERE tenant_id = anon` (0000…). Selectionnez des dossiers pour export CSV ou visualisation PDF.
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
          {selected.size > 0 && (
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={loadingExport}
              className="ml-2"
            >
              {loadingExport ? "Export…" : `Export CSV (${selected.size})`}
            </Button>
          )}
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
                <th>Actions</th>
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
                  <td className="text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => toggleSelect(d.id)}
                      className="text-gray-600 hover:text-navy"
                    >
                      {isSelected(d.id) ? "✓" : "∎"}
                    </Button>{' '}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => window.open(`/dossier/${d.id}`, "_blank")}
                      className="text-gray-600 hover:text-navy ml-1"
                    >
                      {d.pdf_r2_key ? "PDF" : "—"}
                    </Button>
                  </td>
                </tr>
              ))}
              {data && data.dossiers.length === 0 && (
                <tr>
                  <td colSpan={11} className="py-8 text-center text-gray-500">
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

      {data && data.dossiers.length > 0 && (
        <Card className="mt-6">
          <h2 className="text-semibold mb-3">Aperçu PDF</h2>
          <div className="overflow-auto">
            {data.dossiers.map((d: any) => (
              <PdfViewer
                key={d.id}
                r2Key={d.pdf_r2_key}
                fallbackText={d.project_name || "Aucun projet"}
                selected={isSelected(d.id)}
                onToggle={() => toggleSelect(d.id)}
              />
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
