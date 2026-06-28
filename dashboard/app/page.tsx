import { loadResults } from "@/lib/loadResults";
import SampleDataBanner from "@/components/SampleDataBanner";
import TokenBreakdownHero from "@/components/TokenBreakdownHero";
import TokenEfficiencyChart from "@/components/TokenEfficiencyChartClient";
import WordVsCharComparison from "@/components/WordVsCharComparison";
import LatencyThroughputChart from "@/components/LatencyThroughputChartClient";
import CostProjectionSection from "@/components/CostProjectionSection";
import MethodologyFooter from "@/components/MethodologyFooter";

export default function Home() {
  const results = loadResults();

  return (
    <main className="min-h-screen bg-ink">
      <SampleDataBanner visible={results.sample_data} />

      <TokenBreakdownHero
        tokenizerEfficiency={results.tokenizer_efficiency}
        baselineLanguage={results.baseline_language}
        languages={results.languages}
      />

      <TokenEfficiencyChart
        tokenizerEfficiency={results.tokenizer_efficiency}
        baselineLanguage={results.baseline_language}
        languages={results.languages}
      />

      <WordVsCharComparison
        tokenizerEfficiency={results.tokenizer_efficiency}
        baselineLanguage={results.baseline_language}
        languages={results.languages}
      />

      <LatencyThroughputChart
        quantizationBenchmark={results.quantization_benchmark}
        languages={results.languages}
      />

      <CostProjectionSection
        costProjection={results.cost_projection}
        baselineLanguage={results.baseline_language}
        languages={results.languages}
      />

      <MethodologyFooter results={results} />
    </main>
  );
}