"use client";

import { useState } from "react";
import type { TokenizerLanguageStats } from "@/lib/types";

const CHIP_COLORS = ["bg-marigold/25 text-marigold", "bg-teal/25 text-teal", "bg-paper/15 text-paper"];

export default function TokenBreakdownHero({
  tokenizerEfficiency,
  baselineLanguage,
  languages,
}: {
  tokenizerEfficiency: Record<string, TokenizerLanguageStats>;
  baselineLanguage: string;
  languages: string[];
}) {
  const nonBaseline = languages.filter((l) => l !== baselineLanguage);
  const [selected, setSelected] = useState(nonBaseline[0] ?? languages[0]);

  const stats = tokenizerEfficiency[selected];
  const baselineStats = tokenizerEfficiency[baselineLanguage];

  return (
    <section className="max-w-5xl mx-auto px-6 pt-16 pb-12">
      <p className="font-mono text-xs tracking-widest2 uppercase text-teal mb-4">
        Indic Inference Lab
      </p>
      <h1 className="font-display font-bold text-4xl md:text-5xl leading-tight text-paper max-w-3xl">
        The same sentence costs more tokens depending on what language it's written in.
      </h1>
      <p className="font-body text-ink2 mt-4 max-w-2xl text-base md:text-lg">
        Below is the same idea, in {baselineLanguage} and in the language you pick — translated by
        professional linguists as part of the FLORES-200 corpus, not paraphrased by us. Watch how many
        pieces the tokenizer breaks each one into.
      </p>

      <div className="flex flex-wrap gap-2 mt-8" role="tablist" aria-label="Select a language to compare">
        {nonBaseline.map((lang) => (
          <button
            key={lang}
            role="tab"
            aria-selected={selected === lang}
            onClick={() => setSelected(lang)}
            className={`font-mono text-sm px-4 py-2 rounded-full border transition-colors ${
              selected === lang
                ? "bg-marigold text-ink border-marigold"
                : "bg-transparent text-ink2 border-rule hover:border-marigold hover:text-paper"
            }`}
          >
            {lang}
          </button>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4 mt-8">
        {/* Baseline column */}
        <div className="bg-surface border border-rule rounded-xl p-6">
          <div className="flex items-baseline justify-between mb-4">
            <span className="font-mono text-xs uppercase tracking-widest2 text-ink2">
              {baselineLanguage} · baseline
            </span>
            <span className="font-mono text-2xl text-paper">
              {baselineStats?.mean_tokens_per_word.toFixed(2)}
              <span className="text-ink2 text-sm"> tok/word</span>
            </span>
          </div>
          <p className="font-body text-sm text-ink2 mb-3">{baselineStats?.sample_sentence}</p>
          <TokenChips tokens={baselineStats?.sample_token_breakdown ?? []} />
        </div>

        {/* Selected language column */}
        <div className="bg-surface border border-marigold/40 rounded-xl p-6">
          <div className="flex items-baseline justify-between mb-4">
            <span className="font-mono text-xs uppercase tracking-widest2 text-marigold">
              {selected}
            </span>
            <span className="font-mono text-2xl text-paper">
              {stats?.mean_tokens_per_word.toFixed(2)}
              <span className="text-ink2 text-sm"> tok/word</span>
            </span>
          </div>
          <p className="font-body text-sm text-ink2 mb-3">{stats?.sample_sentence}</p>
          <TokenChips tokens={stats?.sample_token_breakdown ?? []} />
          <p className="font-mono text-sm text-marigold mt-4">
            {stats?.ratio_vs_baseline.toFixed(2)}× the tokens of {baselineLanguage}, same sentence.
          </p>
        </div>
      </div>
    </section>
  );
}

function TokenChips({ tokens }: { tokens: string[] }) {
  return (
    <div className="flex flex-wrap gap-1" aria-label="Token breakdown">
      {tokens.map((tok, i) => (
        <span
          key={i}
          className={`font-mono text-xs px-1.5 py-0.5 rounded ${CHIP_COLORS[i % CHIP_COLORS.length]}`}
        >
          {tok.trim() === "" ? "·" : tok}
        </span>
      ))}
    </div>
  );
}
