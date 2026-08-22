"use client";

const plans = [
  { id: "free", name: "Free", price: "0 DZD", quota: "1 dossier / mois", cta: "Commencer", features: ["1 G12/G50 preview", "Sans PDF download (watermark)", "Guides fiscaux"] },
  { id: "starter", name: "Starter", price: "2 900 DZD/mois", quota: "10 docs / mois", cta: "Choisir Starter", features: ["7 formulaires DGI PDF", "Faisabilité offline", "Export PDF"] },
  { id: "pro", name: "Pro", price: "5 900 DZD/mois", quota: "∞ (fair-use 100)", cta: "Passer Pro — Recommandé", features: ["LLM Groq online", "Batch 10", "AAPI 1500", "Queue prioritaire"], highlight: true },
  { id: "business", name: "Business", price: "12 900 DZD/mois", quota: "∞ (300) + API + whitelabel", cta: "Business", features: ["API access", "Whitelabel PDF", "Webhooks"] },
];
import { useState } from "react";
import { createCheckout } from "@/lib/billing";

export default function Pricing() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onCheckout(plan: string) {
    if (plan === "free") {
      window.location.href = "/dashboard";
      return;
    }
    setLoading(plan);
    setError(null);
    try {
      const r = await createCheckout(plan, "monthly");
      // In mock gateway, payment_url is /billing/mock-pay → simulate webhook then redirect to success
      window.location.href = r.payment_url;
    } catch (e: any) {
      setError(String(e.message || e));
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="text-3xl font-bold text-navy">Tarifs — Chargily Pay (BaridiMob/CIB/Dahabiya)</h1>
      <p className="text-sm text-gray-600">
        Yearly = 10× mensuel (2 mois offerts). Webhook HMAC <code>X-Chargily-Signature</code> → <code>users.subscription_until</code> (extend-until, idempotent).
      </p>
      {error && <div className="mt-4 rounded bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <div className="mt-8 grid md:grid-cols-4 gap-6">
        {plans.map((p) => (
          <div key={p.id} className={`rounded-xl border p-6 ${p.highlight ? "border-gold shadow-lg" : ""}`}>
            <h3 className="font-bold">{p.name}</h3>
            <p className="text-2xl font-bold text-navy mt-2">{p.price}</p>
            <p className="text-xs text-gray-500">{p.quota}</p>
            <ul className="mt-4 text-sm space-y-1">
              {p.features.map((f) => <li key={f}>• {f}</li>)}
            </ul>
            <button
              onClick={() => onCheckout(p.id)}
              disabled={loading === p.id}
              className={`mt-6 block w-full text-center rounded py-2 font-semibold ${p.highlight ? "bg-gold text-navy" : "bg-navy text-white"} disabled:opacity-50`}
            >
              {loading === p.id ? "..." : p.cta}
            </button>
            {p.id !== "free" && <p className="mt-2 text-xs text-gray-500">→ POST /billing/checkout → pay.chargily.dz → webhook → GET /billing/me</p>}
          </div>
        ))}
      </div>
      <p className="mt-6 text-xs text-gray-500">
        Entitlements: <code>require_entitlement</code> compte <code>jobs WHERE tenant_id=uid AND created_at &gt; month_start</code> → 402 (plan) / 429 (quota). Mock: <code>/billing/mock-pay?checkout_id=…</code> → simulate <code>POST /billing/webhook {"{"}checkout_id,status:"paid"{"}"}</code>
      </p>
    </div>
  );
}
