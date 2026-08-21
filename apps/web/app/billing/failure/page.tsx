export default function BillingFailure({ searchParams }: { searchParams: { checkout_id?: string } }) {
  return (
    <div className="mx-auto max-w-xl px-6 py-12">
      <h1 className="text-2xl font-bold text-red-700">Paiement échoué</h1>
      <p className="text-sm text-gray-600">Checkout: <code>{searchParams.checkout_id || "—"}</code></p>
      <p className="mt-4 text-sm">Le paiement via Chargily (BaridiMob/CIB) n&apos;a pas abouti. Réessayez ou contactez le support.</p>
      <a href="/pricing" className="mt-4 inline-block rounded border px-4 py-2">Retour tarifs</a>
    </div>
  );
}
