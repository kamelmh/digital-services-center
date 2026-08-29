"use client";

import { useSearchParams } from "next/navigation";
import { useState } from "react";

export default function MockPayPage() {
  const searchParams = useSearchParams();
  const checkoutId = searchParams.get("checkout_id") || "unknown";
  const [status, setStatus] = useState<"idle" | "loading" | "done">("idle");
  const [result, setResult] = useState<string | null>(null);

  const simulatePayment = async () => {
    setStatus("loading");
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiBase}/billing/webhook`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Chargily-Signature": "mock-signature",
        },
        body: JSON.stringify({
          checkout_id: checkoutId,
          status: "paid",
          amount: 2900,
          currency: "DZD",
          plan: "starter",
          metadata: { checkout_id: checkoutId },
        }),
      });
      const data = await res.json();
      setResult(JSON.stringify(data, null, 2));
      setStatus("done");
    } catch (err) {
      setResult(`Error: ${err}`);
      setStatus("done");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Mock Payment
        </h1>
        <p className="text-gray-600 mb-6">
          This page simulates a Chargily checkout for local testing. In
          production, this redirects to{" "}
          <code className="bg-gray-100 px-1 rounded">pay.chargily.dz</code>.
        </p>

        <div className="bg-gray-50 rounded-md p-4 mb-6">
          <p className="text-sm text-gray-500">Checkout ID</p>
          <p className="font-mono text-sm text-gray-900 break-all">
            {checkoutId}
          </p>
        </div>

        <button
          onClick={simulatePayment}
          disabled={status === "loading"}
          className="w-full bg-emerald-600 text-white py-3 px-4 rounded-md font-medium hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {status === "loading" ? "Processing..." : "Simulate Payment (Paid)"}
        </button>

        {result && (
          <div className="mt-6 bg-gray-50 rounded-md p-4">
            <p className="text-sm text-gray-500 mb-2">Webhook Response</p>
            <pre className="text-xs font-mono text-gray-700 whitespace-pre-wrap overflow-auto max-h-48">
              {result}
            </pre>
          </div>
        )}

        {status === "done" && (
          <a
            href="/pricing"
            className="mt-4 block text-center text-sm text-blue-600 hover:underline"
          >
            ← Back to Pricing
          </a>
        )}
      </div>
    </div>
  );
}
