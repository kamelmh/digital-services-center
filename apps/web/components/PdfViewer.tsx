"use client";

export function PdfViewer({ url, title }: { url: string; title?: string }) {
  if (!url) return null;
  // R2 presigned URL (15m) or local generated_output path
  const isLocal = url.startsWith("C:") || url.startsWith("/tmp") || url.includes("generated_output");
  return (
    <div className="rounded border overflow-hidden">
      <div className="flex justify-between items-center bg-navy px-4 py-2 text-white text-sm">
        <span>{title || "PDF — Tahoma Arabic"}</span>
        <a href={url} target="_blank" className="text-gold underline">
          Ouvrir / Télécharger
        </a>
      </div>
      {isLocal ? (
        <div className="p-4 text-sm text-gray-600">PDF généré localement: <code>{url}</code> — en SaaS ce sera une URL R2 presigned (boto3, 15m).</div>
      ) : (
        <iframe src={url} className="h-[700px] w-full" title={title} />
      )}
    </div>
  );
}
