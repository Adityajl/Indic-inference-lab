import type { TokenizerLanguageStats } from "@/lib/types";

export default function WordVsCharComparison({
  tokenizerEfficiency,
  baselineLanguage,
  languages,
}: {
  tokenizerEfficiency: Record<string, TokenizerLanguageStats>;
  baselineLanguage: string;
  languages: string[];
}) {
  const baseline = tokenizerEfficiency[baselineLanguage];

  return (
    <section className="max-w-5xl mx-auto px-6 py-12 border-t border-rule">
      <h2 className="font-display font-semibold text-2xl text-paper mb-1">
        Why word-level and character-level ratios disagree
      </h2>
      <p className="font-body text-ink2 text-sm mb-6 max-w-2xl">
        Tokens-per-word can make some languages look far worse than others — partly from
        tokenizer quality, partly because some languages just have longer "words." Comparing
        per character separates the two effects.
      </p>

      <div className="bg-surface border border-rule rounded-xl overflow-hidden">
        <table className="w-full font-mono text-sm">
          <thead>
            <tr className="border-b border-rule text-ink2 text-xs uppercase tracking-widest2">
              <th className="text-left px-4 py-3">Language</th>
              <th className="text-right px-4 py-3">tok/word ratio</th>
              <th className="text-right px-4 py-3">tok/char ratio</th>
              <th className="text-right px-4 py-3">chars/word</th>
            </tr>
          </thead>
          <tbody>
            {languages.map((lang) => {
              const stats = tokenizerEfficiency[lang];
              const tokPerCharRatio = baseline && stats
                ? stats.mean_tokens_per_char / baseline.mean_tokens_per_char
                : 1;
              return (
                <tr key={lang} className="border-b border-rule/60 last:border-0">
                  <td className="px-4 py-2.5 text-paper">{lang}</td>
                  <td className="px-4 py-2.5 text-right text-marigold">
                    {stats?.ratio_vs_baseline.toFixed(2)}×
                  </td>
                  <td className="px-4 py-2.5 text-right text-teal">
                    {tokPerCharRatio.toFixed(2)}×
                  </td>
                  <td className="px-4 py-2.5 text-right text-ink2">
                    {stats?.chars_per_word?.toFixed(1) ?? "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="font-body text-xs text-ink2/70 mt-4 max-w-2xl">
        Tamil's word-level ratio looks far higher than Hindi's, but per character they're
        close — Tamil is agglutinative, so grammatical particles fuse onto root words without
        spaces, making whitespace-split "words" longer regardless of tokenizer quality. The
        character-level ratio is the more language-agnostic measure of tokenizer efficiency.
      </p>
    </section>
  );
}