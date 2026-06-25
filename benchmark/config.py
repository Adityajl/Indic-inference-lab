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
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

# ---------------------------------------------------------------------------
# Languages under test
# ---------------------------------------------------------------------------
# Keys are human-readable labels used in the dashboard.
# Values double as both FLORES language codes AND the per-language config
# name on openlanguagedata/flores_plus (they use the same ISO 639-3 + script
# code convention, e.g. "hin_Deva").
LANGUAGES = {
    "English":  "eng_Latn",
    "Hindi":    "hin_Deva",
    "Tamil":    "tam_Taml",
    "Bengali":  "ben_Beng",
    "Marathi":  "mar_Deva",
}
BASELINE_LANGUAGE = "English"

# ---------------------------------------------------------------------------
# FLORES+ dataset settings
# ---------------------------------------------------------------------------
# facebook/flores is deprecated and no longer loadable on datasets>=4.0
# (HF dropped support for "loading script" datasets entirely). This is its
# official, actively-maintained, Parquet-native replacement.
FLORES_DATASET = "openlanguagedata/flores_plus"
FLORES_SPLIT = "devtest"        # parallel sentences, not used in any model's training
NUM_SENTENCES = 200              # how many aligned sentences to use

# ---------------------------------------------------------------------------
# Benchmark settings
# ---------------------------------------------------------------------------
NUM_BENCHMARK_PROMPTS = 30
MAX_NEW_TOKENS = 64
NUM_WARMUP_RUNS = 3
BATCH_SIZE = 1

# ---------------------------------------------------------------------------
# Cost projection settings
# ---------------------------------------------------------------------------
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