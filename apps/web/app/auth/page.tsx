"use client";
import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";

export default function AuthPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");

  async function signIn() {
    if (process.env.NEXT_PUBLIC_SUPABASE_URL === "mock") {
      setMsg("Mock auth — OTP sent (dev). POST /auth/login → JWT 72h");
      return;
    }
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setMsg(error ? error.message : "Connecté — JWT stocké, RLS tenant_id = auth.uid()");
  }

  return (
    <div className="mx-auto max-w-md px-6 py-12">
      <h1 className="text-2xl font-bold">Connexion — Supabase Auth 50k MAU</h1>
      <p className="text-sm text-gray-600">JWT HS256, refresh rotation, `tenant_id` RLS. Fallback `AUTH_REQUIRED=0` pour exe offline.</p>
      <input className="mt-4 w-full rounded border px-3 py-2" placeholder="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input className="mt-2 w-full rounded border px-3 py-2" placeholder="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button onClick={signIn} className="mt-4 w-full rounded bg-navy py-2 text-white">Se connecter</button>
      <p className="mt-3 text-sm text-gray-600">{msg}</p>
      <p className="mt-6 text-xs text-gray-500">Google OAuth: `supabase.auth.signInWithOAuth({"provider":"google"})` — à activer dans Supabase dashboard.</p>
    </div>
  );
}
