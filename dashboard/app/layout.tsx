import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Indic Inference Lab — Tokenization & Quantization Benchmark",
  description:
    "Measuring tokens-per-word and FP16 vs INT8 inference latency for Hindi, Tamil, Bengali, and Marathi against an English baseline, on the parallel FLORES-200 corpus.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
