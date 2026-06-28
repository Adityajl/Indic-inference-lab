"use client";

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid,
} from "recharts";
import type { QuantizationLanguageStats } from "@/lib/types";

export default function LatencyThroughputChart({
  quantizationBenchmark,
  languages,
}: {
  quantizationBenchmark: Record<string, QuantizationLanguageStats>;
  languages: string[];
}) {
  const data = languages.map((lang) => {
    const entry = quantizationBenchmark[lang];
    return {
      language: lang,
      fp16: entry?.fp16?.mean_latency_s ?? 0,
      int8: entry?.int8?.mean_latency_s ?? 0,
      speedup: entry?.latency_speedup ?? null,
    };
  });

  return (
    <section className="max-w-5xl mx-auto px-6 py-12 border-t border-rule">
      <h2 className="font-display font-semibold text-2xl text-paper mb-1">
        FP16 vs INT8 latency, by language
      </h2>
      <p className="font-body text-ink2 text-sm mb-6 max-w-2xl">
        Same hardware, same prompts, same generation length per language — only the
        quantization changes between bars.
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
                value: "mean latency (s)", angle: -90, position: "insideLeft",
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
              formatter={(value: number, name: string) => [`${value.toFixed(2)} s`, name.toUpperCase()]}
            />
            <Legend
              wrapperStyle={{ fontFamily: "IBM Plex Mono", fontSize: 12, color: "#8B8F9C" }}
            />
            <Bar dataKey="fp16" name="FP16" fill="#8B8F9C" radius={[4, 4, 0, 0]} />
            <Bar dataKey="int8" name="INT8" fill="#4FB8AE" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mt-4">
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
        Decode speed above is per-token, so it stays roughly flat across languages — the real
        cost difference shows up in how many tokens each language needs for the same content,
        covered next.
      </p>
    </section>
  );
}
