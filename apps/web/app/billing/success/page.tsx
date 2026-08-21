"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getBillingMe } from "@/lib/billing";

export default function BillingSuccess() {
  const params = useSearchParams();
  const checkoutId = params.get("checkout_id");
  const [me, setMe] = useState<any>(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    let t: any;
    async function poll() {
      try {
        const m = await getBillingMe();
        setMe(m);
        // If still free and we have checkout_id, the webhook may still be processing — poll 5×
        if (m.subscription === "free" && checkoutId && count < 5) {
          t = setTimeout(() => setCount((c) => c + 1), 1500);
        }
      } catch {}
    }
    poll();
    return () => clearTimeout(t);
  }, [checkoutId, count]);

  return (
    <div className="mx-auto max-w-xl px-6 py-12">
      <h1 className="text-2xl font-bold text-navy">Paiement réussi ✓</h1>
      <p className="text-sm text-gray-600">Checkout: <code>{checkoutId}</code></p>
      {me ? (
        <div className="mt-4 rounded border p-4">
          <p>Abonnement: <b>{me.subscription}</b> (quota {me.quota}/mois)</p>
          <p className="text-sm">Valable jusqu&apos;au: {me.until || "—"}</p>
          <a href="/dashboard" className="mt-4 inline-block rounded bg-navy px-4 py-2 text-white">Aller au Dashboard →</a>
        </div>
      ) : (
        <p className="mt-4 text-sm">Vérification de l&apos;abonnement… (webhook HMAC, idempotent, extend-until)</p>
      )}
      <p className="mt-4 text-xs text-gray-500">Mock: si gateway=mock, le webhook est simulé via <code>POST /billing/webhook {"{"}checkout_id,status:"paid"{"}"}</code> et est idempotent (already_processed).</p>
    </div>
  );
}
