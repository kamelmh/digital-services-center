import * as React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: (string | undefined)[]) {
  return twMerge(clsx(inputs));
}

export function Button({ className, variant = "default", ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "ghost" }) {
  const base = "inline-flex items-center justify-center rounded px-4 py-2 text-sm font-semibold transition";
  const styles = variant === "ghost" ? "border hover:bg-gray-50" : "bg-navy text-white hover:bg-navy/90";
  return <button className={cn(base, styles, className)} {...props} />;
}

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-xl border bg-white p-6 shadow-sm", className)} {...props} />;
}
