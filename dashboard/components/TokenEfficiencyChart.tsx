"use client";

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";
import type { TokenizerLanguageStats } from "@/lib/types";

export default function TokenEfficiencyChart({
  tokenizerEfficiency,
  baselineLanguage,
  languages,
}: {
  tokenizerEfficiency: Record<string, TokenizerLanguageStats>;
  baselineLanguage: string;
  languages: string[];
}) {
  const data = languages.map((lang) => ({
    language: lang,
    tokensPerWord: tokenizerEfficiency[lang]?.mean_tokens_per_word ?? 0,
    isBaseline: lang === baselineLanguage,
  }));

  return (
    <section className="max-w-5xl mx-auto px-6 py-12 border-t border-rule">
      <h2 className="font-display font-semibold text-2xl text-paper mb-1">
        Tokens per word, by language
      </h2>
      <p className="font-body text-ink2 text-sm mb-6 max-w-2xl">
        Measured on {languages.length} languages from the same FLORES-200 parallel sentences —
        every bar represents the same underlying content.
      </p>
      <div className="bg-surface border border-rule rounded-xl p-4" style={{ height: 320 }}>
        <ResponsiveContainer width={700} height={300}>
          <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid stroke="#2A2E3A" vertical={false} />
            <XAxis
              dataKey="language"
              tick={{ fill: "#8B8F9C", fontFamily: "IBM Plex Mono", fontSize: 12 }}
              axisLine={{ stroke: "#2A2E3A" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#8B8F9C", fontFamily: "IBM Plex Mono", fontSize: 12 }}
              axisLine={{ stroke: "#2A2E3A" }}
              tickLine={false}
              label={{
                value: "tokens / word", angle: -90, position: "insideLeft",
                fill: "#8B8F9C", fontFamily: "IBM Plex Mono", fontSize: 11,
              }}
            />
            <Tooltip
              cursor={{ fill: "#2A2E3A" }}
              contentStyle={{
                backgroundColor: "#1B1E29", border: "1px solid #2A2E3A",
                fontFamily: "IBM Plex Mono", fontSize: 12, borderRadius: 8,
              }}
              labelStyle={{ color: "#EDEDF0" }}
              formatter={(value: number) => [`${value.toFixed(2)} tok/word`, ""]}
            />
            <Bar dataKey="tokensPerWord" radius={[4, 4, 0, 0]}>
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.isBaseline ? "#4FB8AE" : "#E8A33D"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex gap-4 mt-3 font-mono text-xs text-ink2">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-teal inline-block" /> baseline ({baselineLanguage})
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-marigold inline-block" /> Indic language
        </span>
      </div>
    </section>
  );
}
