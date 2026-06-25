"""
Benchmarks FP16 vs INT8 (bitsandbytes) latency and throughput, using the same
prompts, same hardware, same generation length for both — the only variable
that changes between runs is the quantization. Run on a GPU (a free Colab T4
is enough for a 1-3B model).

Prompts are drawn from the FLORES parallel corpus per language, so the
benchmark is broken out by language rather than reporting one aggregate
number — that's the whole point of this project: generic benchmarks hide
exactly the gap this measures.

Run directly to test in isolation (after download_flores.py has run):
    python quantize_and_benchmark.py
"""

import gc
import json
import os
import sys
import time
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def load_corpus():
    with open(config.PARALLEL_CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _free_gpu_memory():
    import torch
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def benchmark_model(model, tokenizer, prompts, max_new_tokens, num_warmup, device):
    """
    Runs sequential single-request generation (batch size 1, matching a
    single-user inference scenario rather than a batched server scenario)
    and times each request individually with CUDA-synchronized wall clock.

    Returns per-request latencies (seconds) and total tokens generated.
    """
    import torch

    latencies = []
    tokens_generated = []

    # Warmup: lets CUDA kernels JIT/cache and CUDNN autotune settle before
    # the timed runs, so the first couple of (slow) calls don't skew p50/p95.
    for i in range(min(num_warmup, len(prompts))):
        inputs = tokenizer(prompts[i], return_tensors="pt").to(device)
        with torch.no_grad():
            model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        input_len = inputs["input_ids"].shape[1]

        if device == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter()

        with torch.no_grad():
            output_ids = model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        if device == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start

        n_generated = output_ids.shape[1] - input_len
        latencies.append(elapsed)
        tokens_generated.append(n_generated)

    return latencies, tokens_generated


def summarize(latencies, tokens_generated):
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    p50 = sorted_lat[int(n * 0.50)] if n else 0.0
    p95 = sorted_lat[min(int(n * 0.95), n - 1)] if n else 0.0
    total_tokens = sum(tokens_generated)
    total_time = sum(latencies)
    return {
        "mean_latency_s": round(statistics.mean(latencies), 4) if latencies else 0.0,
        "p50_latency_s": round(p50, 4),
        "p95_latency_s": round(p95, 4),
        "tokens_per_second": round(total_tokens / total_time, 2) if total_time > 0 else 0.0,
        "num_requests": n,
        "total_tokens_generated": total_tokens,
    }


def run():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

    if not torch.cuda.is_available():
        print("WARNING: no CUDA GPU detected. INT8 quantization via bitsandbytes "
              "needs a GPU — on CPU this script will run but FP16 vs INT8 won't "
              "be a meaningful comparison. Use a Colab T4 runtime.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    corpus_data = load_corpus()
    languages = corpus_data["languages"]

    print(f"Loading tokenizer for {config.MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    results = {"model": config.MODEL_NAME, "device": device, "per_language": {}}

    # ---- FP16 baseline ----
    print(f"\nLoading {config.MODEL_NAME} in FP16...")
    model_fp16 = AutoModelForCausalLM.from_pretrained(
        config.MODEL_NAME,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    ).to(device)
    model_fp16.eval()

    fp16_results = {}
    for label, sentences in languages.items():
        prompts = sentences[:config.NUM_BENCHMARK_PROMPTS]
        if not prompts:
            continue
        print(f"  [FP16] Benchmarking {label} ({len(prompts)} prompts)...")
        latencies, tokens_gen = benchmark_model(
            model_fp16, tokenizer, prompts,
            config.MAX_NEW_TOKENS, config.NUM_WARMUP_RUNS, device,
        )
        fp16_results[label] = summarize(latencies, tokens_gen)

    del model_fp16
    _free_gpu_memory()

    # ---- INT8 quantized ----
    print(f"\nLoading {config.MODEL_NAME} in INT8 (bitsandbytes)...")
    if device == "cuda":
        # Newer `transformers` versions removed the `load_in_8bit=True` shorthand
        # shim on from_pretrained() -- it now has to be passed as an explicit
        # BitsAndBytesConfig, or it gets forwarded as a raw kwarg into the model
        # constructor and crashes with a TypeError.
        quant_config = BitsAndBytesConfig(load_in_8bit=True)
        model_int8 = AutoModelForCausalLM.from_pretrained(
            config.MODEL_NAME, quantization_config=quant_config, device_map="auto",
        )
    else:
        print("Skipping INT8 stage — bitsandbytes 8-bit inference requires CUDA.")
        model_int8 = None

    int8_results = {}
    if model_int8 is not None:
        model_int8.eval()
        for label, sentences in languages.items():
            prompts = sentences[:config.NUM_BENCHMARK_PROMPTS]
            if not prompts:
                continue
            print(f"  [INT8] Benchmarking {label} ({len(prompts)} prompts)...")
            latencies, tokens_gen = benchmark_model(
                model_int8, tokenizer, prompts,
                config.MAX_NEW_TOKENS, config.NUM_WARMUP_RUNS, device,
            )
            int8_results[label] = summarize(latencies, tokens_gen)
        del model_int8
        _free_gpu_memory()

    # ---- Combine + compute speedup per language ----
    for label in languages:
        fp16_stats = fp16_results.get(label)
        int8_stats = int8_results.get(label)
        entry = {"fp16": fp16_stats, "int8": int8_stats}
        if fp16_stats and int8_stats and int8_stats["mean_latency_s"] > 0:
            entry["latency_speedup"] = round(
                fp16_stats["mean_latency_s"] / int8_stats["mean_latency_s"], 3
            )
            entry["throughput_speedup"] = round(
                int8_stats["tokens_per_second"] / fp16_stats["tokens_per_second"], 3
            ) if fp16_stats["tokens_per_second"] > 0 else None
        results["per_language"][label] = entry

    print("\nFP16 vs INT8 summary (mean latency, tokens/sec):")
    for label, entry in results["per_language"].items():
        fp16 = entry.get("fp16") or {}
        int8 = entry.get("int8") or {}
        print(f"  {label:10s} FP16: {fp16.get('mean_latency_s', '-'):>7} s / "
              f"{fp16.get('tokens_per_second', '-'):>6} tok/s   "
              f"INT8: {int8.get('mean_latency_s', '-'):>7} s / "
              f"{int8.get('tokens_per_second', '-'):>6} tok/s   "
              f"speedup: {entry.get('latency_speedup', '-')}")

    out_path = os.path.join(config.RESULTS_DIR, "quantization_benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nWrote benchmark results to {out_path}")
    return results


if __name__ == "__main__":
    run()