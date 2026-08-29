"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { supabase, isMockAuth } from "@/lib/supabaseClient";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function AuthPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errs, setErrs] = useState<{ email?: string; password?: string }>({});
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [ok, setOk] = useState(false);

  function validate() {
    const e: typeof errs = {};
    if (!emailRe.test(email)) e.email = "Email invalide (format EmailStr requis).";
    if (password.length < 8) e.password = "Mot de passe ≥ 8 caractères.";
    setErrs(e);
    return Object.keys(e).length === 0;
  }

  async function signIn(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setMsg("");
    try {
      if (!isMockAuth()) {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw new Error(error.message);
        const token = (data as any)?.session?.access_token;
        if (!token) throw new Error("Connexion réussie mais session sans token.");
        localStorage.setItem("dsc_jwt", token);
        document.cookie = `dsc_jwt=${token}; path=/; max-age=${72 * 3600}; SameSite=Lax`;
        setOk(true);
        setMsg("Connecté — JWT stocké, RLS tenant_id = auth.uid()");
        router.push("/dashboard");
        return;
      }
      const res = await fetch(`${API}/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.detail || body.message || `Erreur ${res.status} — /v1/auth/login manquant côté API (ajouter route auth).`);
      const token = body.access_token || body.token || body.jwt;
      if (!token) throw new Error("Réponse API sans token (attendu {access_token}).");
      localStorage.setItem("dsc_jwt", token);
      document.cookie = `dsc_jwt=${token}; path=/; max-age=${72 * 3600}; SameSite=Lax`;
      setOk(true);
      setMsg("Connecté (mock → JWT 72h stocké)");
      router.push("/dashboard");
    } catch (err: any) {
      setMsg(err?.message || "Erreur de connexion.");
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem("dsc_jwt");
    document.cookie = "dsc_jwt=; path=/; max-age=0";
    try { (supabase as any)?.auth?.signOut?.(); } catch {}
    setOk(false);
    setMsg("Déconnecté.");
  }

  return (
    <div className="mx-auto max-w-md px-6 py-12">
      <h1 className="text-2xl font-bold">Connexion — Supabase Auth 50k MAU</h1>
      <p className="text-sm text-gray-600">JWT HS256, refresh rotation, <code>tenant_id</code> RLS. Fallback <code>AUTH_REQUIRED=0</code> pour exe offline.</p>
      <form onSubmit={signIn} noValidate className="mt-4 space-y-2">
        <input className={`w-full rounded border px-3 py-2 ${errs.email ? "border-red-500" : ""}`} placeholder="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} aria-invalid={!!errs.email} />
        {errs.email && <p className="text-xs text-red-600">{errs.email}</p>}
        <input className={`w-full rounded border px-3 py-2 ${errs.password ? "border-red-500" : ""}`} placeholder="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} aria-invalid={!!errs.password} />
        {errs.password && <p className="text-xs text-red-600">{errs.password}</p>}
        <button type="submit" disabled={loading} className="w-full rounded bg-navy py-2.5 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed">{loading ? "Connexion…" : "Se connecter"}</button>
      </form>
      {msg && <p className={`mt-3 text-sm ${ok ? "text-green-700" : "text-red-600"}`}>{msg}</p>}
      {ok ? <button onClick={logout} className="mt-3 w-full rounded border py-2 text-sm font-semibold hover:bg-gray-50">Se déconnecter</button> : <Link href="/pricing" className="mt-4 inline-block text-sm text-navy underline underline-offset-4">Voir les tarifs →</Link>}
      <p className="mt-6 text-xs text-gray-500">Google OAuth: <code>supabase.auth.signInWithOAuth({"provider":"google"})</code> — activer dans Supabase dashboard.</p>
      <p className="mt-1 text-xs text-gray-400">API: Authorization: Bearer {"<jwt>"} depuis localStorage <code>dsc_jwt</code>. Mock: POST {API}/v1/auth/login → JWT 72h.</p>
    </div>
  );
}
