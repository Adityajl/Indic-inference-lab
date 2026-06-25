import json
import os
import platform
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from data.download_flores import download_flores
import tokenizer_analysis
import quantize_and_benchmark


def get_hardware_info():
    info = {"python_version": platform.python_version(), "platform": platform.platform()}
    try:
        import torch
        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_total_memory_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 1)
    except ImportError:
        pass
    return info


def compute_cost_projection(tokenizer_results, words_per_request=50):
    per_language = tokenizer_results["per_language"]
    price_per_token = config.ASSUMED_USD_PER_1K_OUTPUT_TOKENS / 1000.0
    projection = {}
    for label, stats in per_language.items():
        est_tokens = round(stats["mean_tokens_per_word"] * words_per_request, 1)
        entry = {"words_in_request": words_per_request, "estimated_tokens": est_tokens, "ratio_vs_baseline": stats.get("ratio_vs_baseline", 1.0)}
        if price_per_token > 0:
            entry["estimated_usd_cost"] = round(est_tokens * price_per_token, 5)
        projection[label] = entry
    return {
        "pricing_configured": price_per_token > 0,
        "note": "Dollar costs shown." if price_per_token > 0 else "No price configured — showing relative token cost only.",
        "per_language": projection,
    }


def run_all():
    print("=" * 70)
    print(f"Model: {config.MODEL_NAME}")
    print("=" * 70)

    print("\n[1/4] Downloading/aligning FLORES+ corpus...")
    corpus_data = download_flores()

    print("\n[2/4] Running tokenizer efficiency analysis...")
    tok_results = tokenizer_analysis.run()

    print("\n[3/4] Running FP16 vs INT8 quantization benchmark...")
    bench_results = quantize_and_benchmark.run()

    print("\n[4/4] Computing cost projection and combining results...")
    cost_projection = compute_cost_projection(tok_results)

    combined = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sample_data": False,
        "fallback_corpus": corpus_data.get("fallback_corpus", False),
        "model": config.MODEL_NAME,
        "languages": list(config.LANGUAGES.keys()),
        "baseline_language": config.BASELINE_LANGUAGE,
        "hardware": get_hardware_info(),
        "methodology": {
            "corpus": f"{config.FLORES_DATASET} ({config.FLORES_SPLIT} split)",
            "num_sentences_for_tokenizer_analysis": config.NUM_SENTENCES,
            "num_prompts_for_latency_benchmark": config.NUM_BENCHMARK_PROMPTS,
            "max_new_tokens_per_request": config.MAX_NEW_TOKENS,
            "batch_size": config.BATCH_SIZE,
            "quantization_method": "bitsandbytes load_in_8bit",
        },
        "tokenizer_efficiency": tok_results["per_language"],
        "quantization_benchmark": bench_results["per_language"],
        "cost_projection": cost_projection,
    }

    with open(config.RESULTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Combined results written to {config.RESULTS_JSON_PATH}")
    if combined["fallback_corpus"]:
        print("\n*** WARNING: fallback_corpus is True. Don't use these numbers on a resume. ***")
    return combined


if __name__ == "__main__":
    run_all()