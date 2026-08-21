import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DSC Digital Services Center — Études de Faisabilité 26-154",
  description: "Générateur d'études de faisabilité conformes Décret 26-154, VAN/TRI, NESDA 0%, AAPI 1500pts. 7 formulaires DGI.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" dir="ltr">
      <body>
        <header className="border-b border-gold/20 bg-navy text-white">
          <div className="mx-auto max-w-6xl flex items-center justify-between px-6 py-4">
            <a href="/" className="font-bold tracking-wide">DSC <span className="text-gold">Digital Services Center</span></a>
            <nav className="flex gap-6 text-sm">
              <a href="/pricing" className="hover:text-gold">Tarifs</a>
              <a href="/dashboard" className="hover:text-gold">Dashboard</a>
              <a href="/auth" className="rounded bg-gold px-4 py-2 text-navy font-semibold">Connexion</a>
            </nav>
          </div>
        </header>
        <main className="min-h-[70vh]">{children}</main>
        <footer className="border-t mt-12 py-8 text-center text-sm text-gray-500">
          DSC Digital Services Center — contact@dsc-dz.com — Décret 26-154 • VAN/TRI 12% • NESDA 0%/7ans • AAPI 1500pts
        </footer>
      </body>
    </html>
  );
}
