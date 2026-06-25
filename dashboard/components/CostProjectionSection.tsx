import type { CostProjectionLanguageStats } from "@/lib/types";

export default function CostProjectionSection({
  costProjection,
  baselineLanguage,
  languages,
}: {
  costProjection: {
    pricing_configured: boolean;
    note: string;
    per_language: Record<string, CostProjectionLanguageStats>;
  };
  baselineLanguage: string;
  languages: string[];
}) {
  const wordsInRequest = costProjection.per_language[baselineLanguage]?.words_in_request ?? 50;

  return (
    <section className="max-w-5xl mx-auto px-6 py-12 border-t border-rule">
      <h2 className="font-display font-semibold text-2xl text-paper mb-1">
        What this costs, per request
      </h2>
      <p className="font-body text-ink2 text-sm mb-6 max-w-2xl">
        For a typical {wordsInRequest}-word request, here's how many tokens each language
        actually needs for the same content. {!costProjection.pricing_configured && (
          <span className="text-ink2/80 italic">{costProjection.note}</span>
        )}
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {languages.map((lang) => {
          const stats = costProjection.per_language[lang];
          const isBaseline = lang === baselineLanguage;
          return (
            <div
              key={lang}
              className={`rounded-lg px-4 py-4 border ${
                isBaseline ? "bg-teal/10 border-teal/40" : "bg-surface border-rule"
              }`}
            >
              <p className="font-mono text-xs uppercase tracking-widest2 text-ink2">{lang}</p>
              <p className="font-mono text-2xl text-paper mt-1">
                {stats?.estimated_tokens ?? "—"}
              </p>
              <p className="font-body text-xs text-ink2">tokens estimated</p>
              {stats?.estimated_usd_cost !== undefined ? (
                <p className="font-mono text-sm text-marigold mt-2">
                  ${stats.estimated_usd_cost.toFixed(5)}
                </p>
              ) : (
                <p className="font-mono text-sm text-marigold mt-2">
                  {stats?.ratio_vs_baseline?.toFixed(2)}×
                </p>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
