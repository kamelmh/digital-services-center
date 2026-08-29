"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
export default function BillingFailure() {
  const params = useSearchParams(); const checkoutId = params.get("checkout_id");
  const [sec, setSec] = useState(3);
  useEffect(()=>{ if(sec<=0){ window.location.href="/pricing"; return; } const id=setTimeout(()=>setSec(s=>s-1),1000); return()=>clearTimeout(id); },[sec]);
  return (
    <div className="mx-auto max-w-xl px-6 py-12 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-100 text-2xl">✕</div>
      <h1 className="mt-4 text-2xl font-bold text-red-700">Paiement échoué — فشل الدفع</h1>
      <p className="text-sm text-gray-600">Checkout: <code className="rounded bg-gray-100 px-1">{checkoutId||"—"}</code></p>
      <p className="mt-4 text-sm text-gray-600">Le paiement via Chargily (BaridiMob/CIB/Dahabiya) n&apos;a pas abouti. Aucun débit — vous pouvez réessayer.</p>
      <p className="mt-2 text-xs text-gray-500">Aucun reçu envoyé. Si débité, contactez support@dsc-dz.com — remboursement sous 48h.</p>
      <p className="mt-6 text-sm text-navy">Redirection vers /pricing dans <b>{sec}s</b>…</p>
      <div className="mt-3 flex justify-center gap-3">
        <a href="/pricing" className="rounded bg-navy px-6 py-2 font-semibold text-white">Retour tarifs</a>
        <a href="/billing/mock-pay" className="rounded border px-6 py-2 text-sm">Réessayer (mock)</a>
      </div>
    </div>
  );
}
