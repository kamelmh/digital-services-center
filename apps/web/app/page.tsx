export default function Landing() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-16">
      <section className="grid md:grid-cols-2 gap-10 items-center">
        <div>
          <h1 className="text-4xl font-bold text-navy leading-tight">
            Études de faisabilité <span className="text-gold">conformes Décret 26-154</span> en 90 secondes
          </h1>
          <p className="mt-4 text-gray-600">
            VAN/TRI à 12% • Seuil 996 unités • NESDA 0% sur 7 ans (1,5 an différé) • AAPI 1500pts • 7 formulaires DGI G12/G50/G4/G11/G29/G1/G8. Offline fallback sans LLM.
          </p>
          <div className="mt-6 flex gap-3">
            <a href="/dashboard" className="rounded bg-navy px-6 py-3 text-white font-semibold">Créer un dossier →</a>
            <a href="/pricing" className="rounded border border-navy px-6 py-3 font-semibold">Voir tarifs</a>
          </div>
          <p className="mt-3 text-xs text-gray-500">55 tests pass • Markdown ↔ PDF 9 champs identiques (±tolérances) • Break-even 996 unités vérifié</p>
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="font-semibold">Offre MVP — Revenue First</h3>
          <ul className="mt-3 text-sm space-y-2 text-gray-700">
            <li>✓ G12/G50/G4/G11/G29/G1/G8 — rendu &lt;500ms, HTML+PDF</li>
            <li>✓ Faisabilité 10 sections + NESDA 9 parties — file 202 → poll</li>
            <li>✓ Calculateurs VAN/TRI/seuil/scenarios — source unique `financial_calculators.py`</li>
            <li>✓ Quality gate 6 checks — <code>financial_viability 0.30</code> si VAN/TRI &lt;0</li>
            <li>✓ PDF Tahoma arabe + R2 presigned 15m</li>
          </ul>
        </div>
      </section>

      <section className="mt-16 grid md:grid-cols-3 gap-6">
        <div className="rounded-lg border p-6">
          <h4 className="font-semibold">1. Déposez</h4>
          <p className="text-sm text-gray-600">Activité, wilaya, investissement. Marge canonique [0.2,0.3] garantit Markdown=PDF.</p>
        </div>
        <div className="rounded-lg border p-6">
          <h4 className="font-semibold">2. Suivez</h4>
          <p className="text-sm text-gray-600">Job <code>queued → running (5→70%) → done 100%</code>. Poll <code>GET /v1/dossiers/jobs/{"{id}"}</code> toutes les 2s.</p>
        </div>
        <div className="rounded-lg border p-6">
          <h4 className="font-semibold">3. Récupérez</h4>
          <p className="text-sm text-gray-600">PDF R2 presigned + dossier JSON. Distinction <em>document quality</em> vs <em>financial viability</em> affichée.</p>
        </div>
      </section>
    </div>
  );
}
