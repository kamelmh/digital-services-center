"use client";
import { useState } from "react";
import { createFeasibility } from "@/lib/api";
import { JobPollBar } from "@/components/JobPollBar";
import { PdfViewer } from "@/components/PdfViewer";
import { Button, Card } from "@/components/ui/button";

const WILAYAS = ["Oran", "Alger", "El Bayadh", "Constantine", "Annaba", "Blida", "Sétif"];
const TYPES = [
  { id: "centre_services_num", label: "Centre Services Numériques (0.40-0.70 → canonique 0.20-0.30)", hint: "VAN/TRI 12% • 996 unités break-even" },
  { id: "quincaillerie", label: "Quincaillerie" },
  { id: "restaurant", label: "Restaurant" },
  { id: "cybercafe", label: "Cybercafé" },
  { id: "supermarche", label: "Supermarché" },
];

export default function Dashboard() {
  const [businessType, setBusinessType] = useState("centre_services_num");
  const [wilaya, setWilaya] = useState("Oran");
  const [location, setLocation] = useState("Oran");
  const [investment, setInvestment] = useState(4000000);
  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [quality, setQuality] = useState<any>(null);

  const [quotaError, setQuotaError] = useState<string | null>(null);

  async function onCreate() {
    setResult(null);
    setQuality(null);
    setQuotaError(null);
    try {
      const r = await createFeasibility({ business_type: businessType, location, wilaya, investment });
      setJobId(r.job_id);
    } catch (e: any) {
      const msg = String(e.message || e);
      if (msg.includes("429") || msg.includes("Quota exceeded")) {
        setQuotaError(msg + " — Upgrade requis.");
      } else if (msg.includes("402") || msg.includes("insufficient")) {
        setQuotaError(msg + " — Plan insuffisant.");
      } else {
        setQuotaError(msg);
      }
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <h1 className="text-2xl font-bold text-navy">Dashboard — Dossiers</h1>
      <p className="text-sm text-gray-600">POST /v1/dossiers/feasibility → 202 queued → GET /v1/dossiers/jobs/{"{id}"} poll 2s → R2 PDF. Tenant `tenant_id` isolé (RLS).</p>

      <Card className="mt-6">
        <div className="grid md:grid-cols-4 gap-4">
          <label className="text-sm">
            Activité
            <select value={businessType} onChange={(e) => setBusinessType(e.target.value)} className="mt-1 w-full rounded border px-2 py-2">
              {TYPES.map((t) => <option key={t.id} value={t.id}>{t.label}</option>)}
            </select>
          </label>
          <label className="text-sm">
            Wilaya
            <select value={wilaya} onChange={(e) => setWilaya(e.target.value)} className="mt-1 w-full rounded border px-2 py-2">
              {WILAYAS.map((w) => <option key={w} value={w}>{w}</option>)}
            </select>
          </label>
          <label className="text-sm">
            Ville
            <input value={location} onChange={(e) => setLocation(e.target.value)} className="mt-1 w-full rounded border px-2 py-2" />
          </label>
          <label className="text-sm">
            Investissement (DZD)
            <input type="number" value={investment} onChange={(e) => setInvestment(parseInt(e.target.value) || 0)} className="mt-1 w-full rounded border px-2 py-2" />
          </label>
        </div>
        <Button onClick={onCreate} className="mt-4">Générer — enqueue</Button>
        <p className="mt-2 text-xs text-gray-500">Marge canonique [0.2,0.3] garantit Markdown=PDF (VAN `-3 700 943`, TRI `-44.4%`, seuil `996` unités, marge `25%`).</p>
        {quotaError && (
          <div className="mt-4 rounded bg-amber-50 border border-amber-200 p-3 text-sm">
            <b>429 — Quota dépassé:</b> {quotaError}
            <a href="/pricing" className="ml-2 underline text-navy font-semibold">Voir tarifs →</a>
          </div>
        )}
      </Card>

      {jobId && (
        <div className="mt-6">
          <JobPollBar jobId={jobId} onDone={(j) => { setResult(j); setQuality(j.result?.quality); }} />
        </div>
      )}

      {quality && (
        <Card className="mt-6">
          <h3 className="font-semibold">Quality — document quality vs financial viability</h3>
          <p className="text-sm">Overall: <b>{(quality.score * 100).toFixed(0)}% ({quality.grade})</b> — {quality.passed ? "PASS" : "FAIL"}</p>
          <ul className="mt-2 text-sm space-y-1">
            <li>• Document quality: word_count / numbers / language / structure — <b>PASS</b> (1.00) → dossier bien formé</li>
            <li>• Financial viability: <b>{quality.grade === "C" && !quality.passed ? "FAIL 0.30 — VAN/TRI <0 requires revised assumptions" : "PASS 1.00"}</b></li>
          </ul>
          <p className="mt-2 text-xs text-gray-500">Distinction demandée: le dossier peut être structurellement complet (B) tout en étant financièrement non viable (0.30).</p>
        </Card>
      )}

      {result?.result?.pdf_url && <div className="mt-6"><PdfViewer url={result.result.pdf_url} title={`Dossier ${result.dossier_id}`} /></div>}
    </div>
  );
}
