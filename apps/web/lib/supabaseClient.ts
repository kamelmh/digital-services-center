import { createClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL || "mock";
const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "mock-anon";

export const supabase = url === "mock" ? ({} as any) : createClient(url, anon);

// For mock dev, auth is bypassed — tenant_id = anon user (see apps/api)
export function isMockAuth() {
  return url === "mock";
}
