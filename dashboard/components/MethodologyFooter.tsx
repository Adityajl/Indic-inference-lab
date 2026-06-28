import type { BenchmarkResults } from "@/lib/types";

export default function MethodologyFooter({ results }: { results: BenchmarkResults }) {
  const { methodology, hardware, model, generated_at_utc, fallback_corpus } = results;

  return (
    <footer className="max-w-5xl mx-auto px-6 py-12 border-t border-rule">
      <h2 className="font-display font-semibold text-xl text-paper mb-4">Methodology</h2>
      <div className="grid md:grid-cols-2 gap-x-12 gap-y-2 font-mono text-sm text-ink2">
        <Row label="Model" value={model} />
        <Row label="Corpus" value={methodology.corpus} />
        <Row label="Sentences analyzed (tokenizer)" value={String(methodology.num_sentences_for_tokenizer_analysis)} />
        <Row label="Prompts per language (latency)" value={String(methodology.num_prompts_for_latency_benchmark)} />
        <Row label="Max new tokens / request" value={String(methodology.max_new_tokens_per_request)} />
        <Row label="Batch size" value={String(methodology.batch_size)} />
        <Row label="Quantization" value={methodology.quantization_method} />
        <Row label="GPU" value={hardware?.gpu_name ? String(hardware.gpu_name) : "not recorded"} />
        <Row label="Generated" value={generated_at_utc} />
      </div>

      {fallback_corpus && (
        <p className="font-mono text-sm text-ember mt-4">
          ⚠ This run used the fallback corpus (FLORES download failed) — treat these numbers as a
          pipeline smoke test, not a reportable result.
        </p>
      )}

      <p className="font-body text-xs text-ink2/70 mt-8 max-w-2xl">
        Tokens-per-word is measured on whitespace-split words, valid for every language above since
        they all use whitespace word boundaries. Latency is wall-clock, single request at a time
        (batch size 1), CUDA-synchronized before and after each timed call, with{" "}
        {String(methodology.batch_size === 1 ? "no" : "some")} batching overlap — this matches a
        single-user inference scenario, not a high-throughput batched server.
      </p>
      <p className="font-body text-xs text-ink2/70 mt-3 max-w-2xl">
        {model} does not officially list Hindi, Tamil, Bengali, or Marathi among its supported
        languages — this measures the cost of using a model without official support for these
        languages, not a categorical claim about all LLMs.
      </p>
    </footer>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 py-1 border-b border-rule/60">
      <span className="text-ink2/70">{label}</span>
      <span className="text-paper text-right">{value}</span>
    </div>
  );
}
