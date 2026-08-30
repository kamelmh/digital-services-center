export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <h1 className="text-4xl font-bold">404 — Page non trouvée</h1>
      <p className="mt-2 text-zinc-500">La page demandée n'existe pas.</p>
      <a href="/" className="mt-6 rounded-lg bg-zinc-900 px-6 py-2.5 text-white hover:bg-zinc-800">Retour à l'accueil</a>
    </main>
  );
}
