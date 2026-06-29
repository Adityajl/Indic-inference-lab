import type { QuantizationLanguageStats } from "@/lib/types";

export default function QuantizationSpeedupCards({
  quantizationBenchmark,
  languages,
}: {
  quantizationBenchmark: Record<string, QuantizationLanguageStats>;
  languages: string[];
}) {
  const data = languages.map((lang) => {
    const entry = quantizationBenchmark[lang];
    return { language: lang, speedup: entry?.latency_speedup ?? null };
  });

  return (
    <section className="max-w-5xl mx-auto px-6 py-12 border-t border-rule">
      <h2 className="font-display font-semibold text-2xl text-paper mb-1">
        FP16 vs INT8 latency, by language
      </h2>
      <p className="font-body text-ink2 text-sm mb-6 max-w-2xl">
        Same hardware, same prompts, same generation length per language — only the
        quantization changes.
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {data.map((d) => {
          const isSlower = d.speedup !== null && d.speedup < 1;
          const displayValue = d.speedup ? (isSlower ? 1 / d.speedup : d.speedup) : null;
          return (
            <div key={d.language} className="bg-surface border border-rule rounded-lg px-3 py-2.5">
              <p className="font-mono text-xs text-ink2 uppercase tracking-widest2">{d.language}</p>
              <p className={`font-mono text-lg mt-1 ${isSlower ? "text-ember" : "text-marigold"}`}>
                {displayValue ? `${displayValue.toFixed(2)}×` : "—"}
              </p>
              <p className="font-body text-xs text-ink2">
                {isSlower ? "slower with INT8" : "faster with INT8"}
              </p>
            </div>
          );
        })}
      </div>
      <p className="font-body text-sm text-ink2/80 mt-4 max-w-2xl">
        Decode speed is per-token, so it stays roughly flat across languages — the real
        cost difference shows up in how many tokens each language needs for the same content,
        covered next.
      </p>
    </section>
  );
}