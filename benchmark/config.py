"""
Central configuration for the Indic Inference Lab benchmark.

Change values here, not inside the pipeline scripts. Everything downstream
(tokenizer analysis, quantization, benchmarking, results JSON) reads from
this file, so a single edit here is enough to re-target a different model
or language set.
"""

import os

# ---------------------------------------------------------------------------
# Model under test
# ---------------------------------------------------------------------------
# Any causal LM on the Hub works. Pick something that fits a free Colab T4
# (≤16GB VRAM) in FP16 — a 1-3B parameter model is the sweet spot.
# Swap this for an Indic-tuned model (e.g. "sarvamai/sarvam-1") to compare
# a generic tokenizer against one built for these languages.
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

# ---------------------------------------------------------------------------
# Languages under test
# ---------------------------------------------------------------------------
# Keys are human-readable labels used in the dashboard.
# Values are FLORES-200 language codes (ISO 639-3 + ISO 15924 script code).
# English is the baseline every other language is compared against.
LANGUAGES = {
    "English":  "eng_Latn",
    "Hindi":    "hin_Deva",
    "Tamil":    "tam_Taml",
    "Bengali":  "ben_Beng",
    "Marathi":  "mar_Deva",
}
BASELINE_LANGUAGE = "English"

# ---------------------------------------------------------------------------
# FLORES-200 dataset settings
# ---------------------------------------------------------------------------
FLORES_DATASET = "facebook/flores"
FLORES_CONFIG = "all"          # single config containing every language as columns
FLORES_SPLIT = "devtest"       # 1012 parallel sentences, not used in any model's training
NUM_SENTENCES = 200             # how many parallel sentences to use (devtest has 1012)

# ---------------------------------------------------------------------------
# Benchmark settings
# ---------------------------------------------------------------------------
NUM_BENCHMARK_PROMPTS = 30      # prompts per language for the latency/throughput run
MAX_NEW_TOKENS = 64             # generation length per prompt — keep modest on free GPU
NUM_WARMUP_RUNS = 3             # untimed runs to let CUDA kernels warm up / JIT settle
BATCH_SIZE = 1                  # sequential requests — matches a single-user inference scenario

# ---------------------------------------------------------------------------
# Cost projection settings
# ---------------------------------------------------------------------------
# Update these if you want the dashboard's cost-per-1000-requests numbers to
# reflect a specific provider's published pricing. Left here, explicitly, so
# nobody mistakes this for a measured number — it's pricing data, not a benchmark result.
ASSUMED_USD_PER_1K_OUTPUT_TOKENS = 0.0  # fill in a real published rate before using this

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BENCHMARK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BENCHMARK_DIR, "data")
RESULTS_DIR = os.path.join(BENCHMARK_DIR, "results")
PARALLEL_CORPUS_PATH = os.path.join(DATA_DIR, "parallel_corpus.json")
RESULTS_JSON_PATH = os.path.join(RESULTS_DIR, "benchmark_results.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
