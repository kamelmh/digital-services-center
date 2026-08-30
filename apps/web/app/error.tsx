"use client";
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <h1 className="text-2xl font-bold">Une erreur est survenue</h1>
      <p className="mt-2 text-sm text-zinc-500">{error.message || "Erreur inattendue."}</p>
      <button onClick={() => reset()} className="mt-6 rounded-lg bg-zinc-900 px-6 py-2.5 text-white hover:bg-zinc-800">Réessayer</button>
    </main>
  );
}
