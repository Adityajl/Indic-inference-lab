export interface TokenizerLanguageStats {
  mean_tokens_per_word: number;
  mean_tokens_per_char: number;
  chars_per_word: number;
  ratio_vs_baseline: number;
  sample_sentence: string;
  sample_token_breakdown: string[];
}
export interface LatencyStats {
  mean_latency_s: number;
  p50_latency_s: number;
  p95_latency_s: number;
  tokens_per_second: number;
}

export interface QuantizationLanguageStats {
  fp16: LatencyStats;
  int8: LatencyStats;
  latency_speedup: number;
  throughput_speedup: number;
}

export interface CostProjectionLanguageStats {
  words_in_request: number;
  estimated_tokens: number;
  ratio_vs_baseline: number;
  estimated_usd_cost?: number;
}

export interface BenchmarkResults {
  generated_at_utc: string;
  sample_data: boolean;
  fallback_corpus: boolean;
  model: string;
  languages: string[];
  baseline_language: string;
  hardware: Record<string, string | number | boolean>;
  methodology: {
    corpus: string;
    num_sentences_for_tokenizer_analysis: number;
    num_prompts_for_latency_benchmark: number;
    max_new_tokens_per_request: number;
    batch_size: number;
    quantization_method: string;
  };
  tokenizer_efficiency: Record<string, TokenizerLanguageStats>;
  quantization_benchmark: Record<string, QuantizationLanguageStats>;
  cost_projection: {
    pricing_configured: boolean;
    note: string;
    per_language: Record<string, CostProjectionLanguageStats>;
  };
}
