%%writefile patch_results.py
"""
Regenerates ONLY the tokenizer_efficiency section (decode fix + chars_per_word)
and patches it into an existing benchmark_results.json -- no GPU involved,
quantization_benchmark and everything else stays exactly as it was.

    python patch_results.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
import tokenizer_analysis


def patch():
    if not os.path.exists(config.PARALLEL_CORPUS_PATH):
        print("parallel_corpus.json not found (new session?) -- re-downloading FLORES+...")
        from data.download_flores import download_flores
        download_flores()

    print("Re-running tokenizer analysis with the offset-mapping fix...")
    fresh_tok_results = tokenizer_analysis.run()

    with open(config.RESULTS_JSON_PATH, "r", encoding="utf-8") as f:
        combined = json.load(f)

    combined["tokenizer_efficiency"] = fresh_tok_results["per_language"]

    with open(config.RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nPatched tokenizer_efficiency into {config.RESULTS_JSON_PATH}")
    print("quantization_benchmark, cost_projection, hardware -- all untouched.")


if __name__ == "__main__":
    patch()