"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getBillingMe } from "@/lib/billing";
export default function BillingSuccess() {
  const params = useSearchParams(); const checkoutId = params.get("checkout_id");
  const [me, setMe] = useState<any>(null); const [poll, setPoll] = useState(0); const [sec, setSec] = useState(3);
  useEffect(()=>{ let t:any; (async()=>{ try{ const m=await getBillingMe(); setMe(m); if(m.subscription==="free"&&checkoutId&&poll<5) t=setTimeout(()=>setPoll(c=>c+1),1500);}catch{} })(); return()=>clearTimeout(t); },[checkoutId,poll]);
  useEffect(()=>{ if(sec<=0){ window.location.href="/dashboard"; return; } const id=setTimeout(()=>setSec(s=>s-1),1000); return()=>clearTimeout(id); },[sec]);
  return (
    <div className="mx-auto max-w-xl px-6 py-12 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-2xl">✓</div>
      <h1 className="mt-4 text-2xl font-bold text-navy">Paiement réussi — تم الدفع</h1>
      <p className="text-sm text-gray-600">Checkout: <code className="rounded bg-gray-100 px-1">{checkoutId||"—"}</code></p>
      {me ? (
        <div className="mt-6 rounded-xl border bg-white p-4 text-left">
          <p>Abonnement: <b className="text-emerald-700">{me.subscription}</b> (quota {me.quota}/mois)</p>
          <p className="text-sm text-gray-600">Valable jusqu&apos;au: {me.until || "—"}</p>
          <p className="mt-2 text-xs text-gray-500">Reçu par email — idempotent webhook HMAC <code>X-Chargily-Signature</code> → extend-until.</p>
        </div>
      ) : (<p className="mt-4 text-sm text-gray-500">Vérification abonnement… (poll {poll}/5)</p>)}
      <p className="mt-6 text-sm text-navy">Redirection vers /dashboard dans <b>{sec}s</b>…</p>
      <a href="/dashboard" className="mt-3 inline-block rounded bg-navy px-6 py-2 font-semibold text-white">Aller au Dashboard →</a>
      <p className="mt-4 text-xs text-gray-400">Un reçu a été envoyé par email. Mock: <code>POST /billing/webhook {"{"}checkout_id,status:&quot;paid&quot;{"}"}</code> idempotent.</p>
    </div>
  );
}
