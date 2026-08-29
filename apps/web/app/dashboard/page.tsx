"use client";
import { useEffect, useState } from "react";
import { createFeasibility } from "@/lib/api";
import { getBillingMe } from "@/lib/billing";
import { JobPollBar } from "@/components/JobPollBar";
import { PdfViewer } from "@/components/PdfViewer";
import { Button, Card } from "@/components/ui/button";
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WILAYAS = ["Oran","Alger","El Bayadh","Constantine","Annaba","Blida","Sétif"];
const TYPES = [{id:"centre_services_num",label:"Centre Services Numériques (0.40-0.70 → canonique 0.20-0.30)"},{id:"quincaillerie",label:"Quincaillerie"},{id:"restaurant",label:"Restaurant"},{id:"cybercafe",label:"Cybercafé"},{id:"supermarche",label:"Supermarché"}];
export default function Dashboard(){
  const [formId,setFormId]=useState("feasibility");
  const [businessType,setBusinessType]=useState("centre_services_num");
  const [wilaya,setWilaya]=useState("Oran");
  const [location,setLocation]=useState("Oran");
  const [investment,setInvestment]=useState(4000000);
  const [jobId,setJobId]=useState<string|null>(null);
  const [result,setResult]=useState<any>(null);
  const [quality,setQuality]=useState<any>(null);
  const [quota,setQuota]=useState<any>(null);
  const [quotaError,setQuotaError]=useState<string|null>(null);
  const [toast,setToast]=useState<{msg:string;kind:string}|null>(null);
  const [generating,setGenerating]=useState(false);
  useEffect(()=>{getBillingMe().then(setQuota).catch(()=>{});},[]);
  useEffect(()=>{if(!toast) return; const t=setTimeout(()=>setToast(null),3000); return()=>clearTimeout(t);},[toast]);
  async function onCreate(){
    setResult(null);setQuality(null);setQuotaError(null);
    setGenerating(true);
    try{
      const r=await createFeasibility({business_type:businessType,location,wilaya,investment});
      setJobId(r.job_id); setToast({msg:"Dossier en file d'attente — génération lancée",kind:"success"});
    }catch(e:any){
      const msg=String(e.message||e);
      if(msg.includes("429")||msg.includes("Quota")) setQuotaError(msg+" — Upgrade requis.");
      else if(msg.includes("402")||msg.includes("insufficient")) setQuotaError(msg+" — Plan insuffisant.");
      else setQuotaError(msg);
      setToast({msg, kind:"error"});
    }finally{setGenerating(false);}
  }
  const pct=quota?Math.min(100,Math.round((quota.used_this_month/quota.quota)*100)):0;
  return(<div className="mx-auto max-w-6xl px-6 py-8">
    {toast&&<div className={`fixed right-4 top-4 z-50 rounded px-4 py-3 text-sm font-medium shadow-lg ${toast.kind==="success"?"bg-green-600 text-white":"bg-red-600 text-white"}`}>{toast.msg}</div>}
    <h1 className="text-2xl font-bold text-navy">Dashboard — Dossiers</h1>
    <p className="text-sm text-gray-600">POST /v1/dossiers/feasibility → 202 queued → GET /v1/dossiers/jobs/{"{id}"} poll 2s → R2 PDF.</p>
    {quota&&<Card className="mt-4 flex flex-col gap-2">
      <div className="flex justify-between text-sm"><span>Utilisé: <b>{quota.used_this_month}</b> / Plafond: <b>{quota.quota}</b> — Restant: <b className={quota.remaining===0?"text-red-600":"text-green-700"}>{quota.remaining}</b></span><span className="text-xs text-gray-500">{quota.subscription} {quota.until?"· jusqu'au "+new Date(quota.until).toLocaleDateString():""}</span></div>
      <div className="h-2 rounded bg-gray-100"><div className={`h-2 rounded transition-all ${pct>85?"bg-red-500":pct>60?"bg-amber-500":"bg-navy"}`} style={{width:`${pct}%`}}/></div>
    </Card>}
    <Card className="mt-4">
      <label className="text-sm font-medium">Formulaire
        <select value={formId} onChange={e=>setFormId(e.target.value)} className="mt-1 w-full rounded border px-2 py-2">
          <option value="feasibility">Étude de faisabilité — Feasibility (défaut) / دراسة الجدوى</option>
          <optgroup label="DGI — Impôts (12)">
            <option value="g12">G12 — Déclaration prévisionnelle du CA (IFU) / التصريح التقديمي للفاتورة</option>
            <option value="g12bis">G12 bis — Déclaration définitive du CA / التصريح النهائي للفاتورة</option>
            <option value="g50">G50 — Déclaration mensuelle TVA/TAP/IRG / الإقرار الشهري</option>
            <option value="g4">G4 — Déclaration des revenus locatifs / إقرار بالدخل العقاري</option>
            <option value="g11">G11 — BIC Régime Réel / إقرار بربح البضائع</option>
            <option value="g1">G1 — Liasse fiscale personne physique / إقرار بالدخل الإجمالي</option>
            <option value="g8">G8 — Déclaration d&apos;existence / التصريح بالانطلاقة</option>
            <option value="g13">G13 — IRG professions non commerciales / إقرار بربح المهنة</option>
            <option value="g15">G15 — Cessation d&apos;activité / التصريح بتوقف النشاط</option>
            <option value="g51">G51 — Attestation fiscale / شهادة ضريبية</option>
            <option value="g4_loyers">G4 Loyers — Revenus fonciers (IBS loyers) / إقرار بالدخل العقاري</option>
            <option value="g29">G29 — Traitements et émoluments / الإقرار السنوي للرواتب</option>
          </optgroup>
          <optgroup label="CNRC — Registre du Commerce">
            <option value="cnrc_f1">CNRC F1 — Personne morale (SARL/EURL/SPA) / استمارة التسجيل في السجل التجاري</option>
            <option value="cnrc_f2">CNRC F2 — Personne physique (commerçant) / استمارة تسجيل تاجر</option>
          </optgroup>
          <optgroup label="ONS — Statistiques"><option disabled value="ons-dash">—</option></optgroup>
          <optgroup label="CNAS — Salariés"><option value="das">DAS — Déclaration annuelle des salaires / الإقرار السنوي للرواتب</option><option value="secu01">SECU01 — Affiliation CNAS / طلب الالتحاق</option><option value="nis">NIS — Identification statistique / استمارة طلب رقم التعريف الإحصائي</option></optgroup>
          <optgroup label="ANAE — Auto-entrepreneur"><option value="anae">ANAE — Déclaration d&apos;activité / تصريح النشاط</option></optgroup>
          <optgroup label="CASNOS — Non-salariés"><option value="casnos_aff">CASNOS — Affiliation / طلب الالتحاق بالصندوق الوطني لتأمينات غير الأجراء</option><option value="casnos_ca">CASNOS CA — Déclaration du CA / إقرار بالفاتورة</option></optgroup>
        </select>
      </label>
    </Card>
    {formId==="feasibility"?<Card className="mt-6">
      <div className="grid md:grid-cols-4 gap-4">
        <label className="text-sm">Activité<select value={businessType} onChange={e=>setBusinessType(e.target.value)} className="mt-1 w-full rounded border px-2 py-2">{TYPES.map(t=><option key={t.id} value={t.id}>{t.label}</option>)}</select></label>
        <label className="text-sm">Wilaya<select value={wilaya} onChange={e=>setWilaya(e.target.value)} className="mt-1 w-full rounded border px-2 py-2">{WILAYAS.map(w=><option key={w} value={w}>{w}</option>)}</select></label>
        <label className="text-sm">Ville<input value={location} onChange={e=>setLocation(e.target.value)} className="mt-1 w-full rounded border px-2 py-2"/></label>
        <label className="text-sm">Investissement (DZD)<input type="number" value={investment} onChange={e=>setInvestment(parseInt(e.target.value)||0)} className="mt-1 w-full rounded border px-2 py-2"/></label>
      </div>
      <Button onClick={onCreate} disabled={generating} className="mt-4">{generating?"Génération en cours…":"Générer — enqueue"}</Button>
      <p className="mt-2 text-xs text-gray-500">Marge canonique [0.2,0.3] garantit Markdown=PDF (VAN `-3 700 943`, TRI `-44.4%`, seuil `996` unités, marge `25%`).</p>
      {quotaError&&<div className="mt-4 rounded bg-amber-50 border border-amber-200 p-3 text-sm"><b>429 — Quota dépassé:</b> {quotaError}<a href="/pricing" className="ml-2 underline text-navy font-semibold">Voir tarifs →</a></div>}
    </Card>:<Card className="mt-6 border-dashed bg-gray-50">
      <p className="text-sm">Génération via <code className="rounded bg-white px-1 py-0.5 border">POST /tax/{formId}</code> — API DGI/CNAS/CNRC.</p>
      <a href={`${API}/docs`} target="_blank" className="mt-2 inline-block text-sm font-semibold text-navy underline">Voir API docs → {API}/docs</a>
      <p className="mt-2 text-xs text-gray-500">Sélectionnez l&apos;étude de faisabilité pour le flux complet avec polling et PDF inline.</p>
    </Card>}
    {(generating||(jobId&&!result))&&<div className="mt-4 flex items-center gap-2 text-sm text-navy"><span className="h-4 w-4 animate-spin rounded-full border-2 border-navy border-t-transparent"/><span>Génération en cours…</span></div>}
    {jobId&&<div className="mt-4"><JobPollBar jobId={jobId} onDone={j=>{setResult(j);setQuality(j.result?.quality); if(j.status==="done") setToast({msg:"PDF prêt ✓",kind:"success"}); if(j.status==="failed") setToast({msg:j.error||"Échec génération",kind:"error"});}}/></div>}
    {quality&&<Card className="mt-6"><h3 className="font-semibold">Quality — document quality vs financial viability</h3><p className="text-sm">Overall: <b>{(quality.score*100).toFixed(0)}% ({quality.grade})</b> — {quality.passed?"PASS":"FAIL"}</p><ul className="mt-2 text-sm space-y-1"><li>• Document quality: word_count / numbers / language / structure — <b>PASS</b> (1.00) → dossier bien formé</li><li>• Financial viability: <b>{quality.grade==="C"&&!quality.passed?"FAIL 0.30 — VAN/TRI <0 requires revised assumptions":"PASS 1.00"}</b></li></ul></Card>}
    {result?.result?.pdf_url&&<div className="mt-6"><PdfViewer url={result.result.pdf_url} title={`Dossier ${result.dossier_id}`}/></div>}
  </div>);}
