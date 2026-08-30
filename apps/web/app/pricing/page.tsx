"use client";
import { useState } from "react";
import { createCheckout } from "@/lib/billing";
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const plans = [
  { id: "free", name: "Free — مجاني", price: "0 DZD", quota: "1 / mois", cta: "Commencer", hi: false },
  { id: "starter", name: "Starter", price: "2 900 DZD/mois", quota: "10 / mois", cta: "Choisir Starter", hi: false },
  { id: "pro", name: "Pro — احترافي", price: "5 900 DZD/mois", quota: "100 / mois", cta: "Passer Pro ✓", hi: true },
  { id: "business", name: "Business", price: "9 900 DZD/mois", quota: "300 + API", cta: "Business", hi: false },
];
const forms = [
  ["G12 IFU", "aperçu", "✓", "✓", "✓"], ["G12 bis", "—", "✓", "✓", "✓"], ["G50 mensuel", "—", "✓", "✓", "✓"],
  ["G4 IBS", "—", "✓", "✓", "✓"], ["G11 BIC", "—", "—", "✓", "✓"], ["G1 revenus", "—", "✓", "✓", "✓"],
  ["G8 existence", "—", "✓", "✓", "✓"], ["G13 BNC", "—", "—", "✓", "✓"], ["G15 cessation", "—", "—", "✓", "✓"],
  ["G51 attestation", "—", "—", "✓", "✓"], ["CNRC F1", "—", "—", "✓", "✓"], ["CNRC F2", "—", "—", "✓", "✓"],
  ["DAS CNAS", "—", "—", "✓", "✓"], ["SECU01", "—", "—", "✓", "✓"], ["NIS ONS", "—", "—", "✓", "✓"],
  ["ANAE", "—", "—", "✓", "✓"], ["CASNOS affil.", "—", "—", "✓", "✓"], ["CASNOS CA", "—", "—", "✓", "✓"],
  ["G4 Loyers", "—", "—", "✓", "✓"], ["G29 salaires", "—", "—", "✓", "✓"],
];
export default function Pricing() {
  const [loading, setLoading] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [quote, setQuote] = useState<string | null>(null);
  async function onCheckout(plan: string) {
    if (plan === "free") { window.location.href = "/dashboard"; return; }
    setLoading(plan); setErr(null);
    try { const r = await createCheckout(plan, "monthly"); if (r.payment_url && r.payment_url.startsWith("https://")) window.location.href = r.payment_url; else setErr("URL de paiement invalide"); }
    catch (e: any) { setErr(String(e.message || e)); } finally { setLoading(null); }
  }
  async function onQuote() {
    setQuote("..."); try {
      const r = await fetch(`${API}/pricing/quote`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ service_keys: ["feasibility_standard"], discount_pct: 0 }) });
      const j = await r.json(); setQuote(j.total ? `Devis: ${j.total.toLocaleString()} DZD — via pricing_calculator.py` : JSON.stringify(j).slice(0,120));
    } catch (e: any) { setQuote("pricing_calculator.py — POST /pricing/quote indisponible: " + String(e.message).slice(0,60)); }
  }
  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-bold text-navy sm:text-3xl">Tarifs — Chargily Pay <span className="text-sm font-normal text-gray-500">(BaridiMob/CIB/Dahabiya)</span></h1>
      <p className="mt-1 text-sm text-gray-600">Annuel = 10× mensuel (2 mois offerts). Prix backend <code>PLANS</code>: 2900/5900/9900 DZD.</p>
      {err && <div className="mt-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{err}</div>}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {plans.map((p) => (
          <div key={p.id} className={`rounded-xl border p-5 ${p.hi ? "border-gold shadow-lg" : "bg-white"}`}>
            <h3 className="font-bold text-navy">{p.name}</h3><p className="mt-1 text-xl font-bold text-navy">{p.price}</p><p className="text-xs text-gray-500">{p.quota}</p>
            <button onClick={() => onCheckout(p.id)} disabled={loading === p.id} className={`mt-4 w-full rounded py-2 text-sm font-semibold ${p.hi ? "bg-gold text-navy" : "bg-navy text-white"} disabled:opacity-50`}>{loading === p.id ? "..." : p.cta}</button>
          </div>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-2"><button onClick={onQuote} className="rounded bg-navy px-4 py-2 text-sm font-semibold text-white">Générer un devis</button><span className="text-xs text-gray-500 self-center">POST {API}/pricing/quote → pricing_calculator.py</span>{quote && <span className="rounded border bg-gray-50 px-2 py-1 text-xs">{quote}</span>}</div>
      <div className="mt-8 overflow-x-auto rounded-xl border">
        <table className="w-full min-w-[600px] text-sm">
          <thead className="sticky top-0 bg-navy text-white"><tr><th className="p-2 text-left">Comparez les plans — مقارنة الخطط</th><th>Free</th><th>Starter</th><th className="bg-gold text-navy">Pro</th><th>Business</th></tr></thead>
          <tbody className="divide-y">
            <tr className="bg-gray-50"><td className="p-2 font-medium">Quota / mois — الحصة</td><td className="text-center">1</td><td className="text-center">10</td><td className="text-center font-bold">100</td><td className="text-center">300+API</td></tr>
            <tr><td className="p-2 font-medium">Prix — السعر</td><td className="text-center">0</td><td className="text-center">2 900 DA</td><td className="text-center font-bold">5 900 DA</td><td className="text-center">9 900 DA</td></tr>
            {forms.map(([n, ...cols]) => (<tr key={n}><td className="p-2">{n}</td>{cols.map((c, i) => (<td key={i} className={`text-center ${c === "✓" ? "text-emerald-600 font-bold" : "text-gray-300"}`}>{c}</td>))}</tr>))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-gray-500">Source prix: <code>apps/api/app/routers/billing.py:PLANS</code> — 20 générateurs. Pro/Business débloquent tout. Whitelabel + API + webhooks = Business uniquement.</p>
    </div>
  );
}
