const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getPlans() {
  const r = await fetch(`${API}/billing/plans`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function createCheckout(plan: string, cycle: "monthly" | "yearly" = "monthly") {
  const r = await fetch(`${API}/billing/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plan, billing_cycle: cycle }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ plan: string; price: number; gateway: string; payment_url: string; checkout_id: string }>;
}

export async function getBillingMe() {
  const r = await fetch(`${API}/billing/me`, { cache: "no-store" });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ tenant_id: string; subscription: string; until: string | null; quota: number }>;
}
