"use client";
import { useSearchParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const OPTS = [
  { id: "starter", label: "Starter", price: 2900, quota: 10 },
  { id: "pro", label: "Pro", price: 5900, quota: 100 },
  { id: "business", label: "Business", price: 9900, quota: 300 },
];
export default function MockPayPage() {
  const sp = useSearchParams(); const router = useRouter();
  const checkoutId = sp.get("checkout_id") || "chk_mock";
  const qPlan = sp.get("plan") as string | null;
  const [plan, setPlan] = useState(qPlan && OPTS.find(o=>o.id===qPlan) ? qPlan : "starter");
  const [status, setStatus] = useState<"idle"|"loading"|"done">("idle");
  const [msg, setMsg] = useState<string | null>(null);
  const [me, setMe] = useState<any>(null);
  const cur = OPTS.find(o=>o.id===plan)!;
  useEffect(()=>{ (async()=>{
    const tok = typeof window!=="undefined"?localStorage.getItem("token")||localStorage.getItem("access_token")||localStorage.getItem("jwt"):"";
    const h:Record<string,string>={}; if(tok) h.Authorization=`Bearer ${tok}`;
    try{ const r=await fetch(`${API}/billing/me`,{headers:h}); if(r.ok) setMe(await r.json()); }catch{}
  })(); },[]);
  async function pay(){
    setStatus("loading"); setMsg(null);
    const tok = typeof window!=="undefined"?localStorage.getItem("token")||localStorage.getItem("access_token")||localStorage.getItem("jwt"):"";
    const headers:Record<string,string>={"Content-Type":"application/json","X-Chargily-Signature":"mock-signature"};
    if(tok) headers.Authorization=`Bearer ${tok}`;
    // tenant_id optional — backend resolves from JWT/checkout; include when available
    const tenant_id = me?.tenant_id||me?.user_id||undefined;
    try{
      const res=await fetch(`${API}/billing/webhook`,{method:"POST",headers,body:JSON.stringify({checkout_id:checkoutId,status:"paid",plan,currency:"DZD",amount:cur.price,tenant_id})});
      const data=await res.json();
      if(!res.ok) throw new Error(JSON.stringify(data));
      setMsg("✓ Paiement simulé — تم الدفع"); setStatus("done");
      setTimeout(()=>router.push(`/billing/success?checkout_id=${checkoutId}`),1200);
    }catch(e:any){ setMsg("✗ "+String(e.message||e).slice(0,180)); setStatus("done"); }
  }
  return (
    <div className="min-h-[70vh] bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md rounded-xl border bg-white p-6 shadow-sm">
        <h1 className="text-xl font-bold text-navy">Paiement Mock — الدفع التجريبي</h1>
        <p className="mt-1 text-xs text-gray-500">Simule Chargily (pay.chargily.dz) en local. Aucun débit réel.</p>
        <div className="mt-4 rounded bg-gray-50 p-3"><p className="text-xs text-gray-500">Checkout ID</p><p className="font-mono text-xs break-all">{checkoutId}</p></div>
        <label className="mt-4 block text-sm font-medium">Plan</label>
        <select value={plan} onChange={e=>setPlan(e.target.value)} className="mt-1 w-full rounded border px-3 py-2 text-sm">
          {OPTS.map(o=><option key={o.id} value={o.id}>{o.label} — {o.price} DZD — {o.quota}/mois</option>)}
        </select>
        <p className="mt-2 text-sm">Prix: <b>{cur.price} DZD</b> · Quota: <b>{cur.quota}/mois</b></p>
        {me && <p className="mt-2 rounded border bg-navy/5 p-2 text-xs">Utilisé ce mois: <b>{me.used_this_month ?? "—"}</b> / Quota {me.quota} · Restant: <b>{me.remaining ?? "—"}</b></p>}
        {!me && <p className="mt-2 text-xs text-gray-400">GET /billing/me — connectez-vous pour voir le quota.</p>}
        <button onClick={pay} disabled={status==="loading"} className="mt-4 w-full rounded bg-navy py-2.5 font-semibold text-white disabled:opacity-50">{status==="loading"?"Traitement...":"Payer (mock) — ادفع"}</button>
        {msg && <div className={`mt-3 rounded p-3 text-sm ${msg.startsWith("✓")?"bg-emerald-50 text-emerald-700 border border-emerald-200":"bg-red-50 text-red-700 border border-red-200"}`}>{msg}</div>}
        {status==="done" && msg?.startsWith("✓") && <p className="mt-2 text-center text-xs text-gray-500">Redirection vers /billing/success…</p>}
        <a href="/pricing" className="mt-4 block text-center text-sm text-gray-600 hover:underline">← Retour tarifs</a>
      </div>
    </div>
  );
}
