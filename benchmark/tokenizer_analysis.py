"""
Measures tokenization efficiency per language on the aligned FLORES corpus.
"""

import json
import os
import sys
import statistics

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def load_corpus():
    if not os.path.exists(config.PARALLEL_CORPUS_PATH):
        raise FileNotFoundError(
            f"No parallel corpus found at {config.PARALLEL_CORPUS_PATH}. "
            f"Run `python data/download_flores.py` first."
        )
    with open(config.PARALLEL_CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_tokenizer(tokenizer, corpus_data):
    languages = corpus_data["languages"]
    results = {}

    for label, sentences in languages.items():
        tokens_per_word_samples = []
        tokens_per_char_samples = []
        total_tokens = 0
        total_words = 0
        total_chars = 0

        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            token_ids = tokenizer.encode(sentence, add_special_tokens=False)
            n_tokens = len(token_ids)
            n_words = len(words)
            n_chars = len(sentence)

            tokens_per_word_samples.append(n_tokens / n_words)
            tokens_per_char_samples.append(n_tokens / max(n_chars, 1))
            total_tokens += n_tokens
            total_words += n_words
            total_chars += n_chars

        # Build one illustrative token breakdown for the dashboard's hero visual.
        sample_sentence = min(sentences, key=lambda s: len(s.split())) if sentences else ""

        # FIX: don't decode token ids one at a time -- byte-level BPE tokens can
        # represent partial multi-byte UTF-8 characters, so decoding them alone
        # produces invalid UTF-8 (mojibake). Instead, ask the tokenizer for each
        # token's character offsets in the ORIGINAL string and slice that --
        # this sidesteps byte-level decode ambiguity entirely.
        encoding = tokenizer(sample_sentence, add_special_tokens=False, return_offsets_mapping=True)
        offsets = encoding["offset_mapping"]
        sample_token_strs = [
            sample_sentence[start:end] if end > start else "·"
            for start, end in offsets
        ]

        results[label] = {
            "mean_tokens_per_word": round(statistics.mean(tokens_per_word_samples), 3),
            "median_tokens_per_word": round(statistics.median(tokens_per_word_samples), 3),
            "stdev_tokens_per_word": round(
                statistics.stdev(tokens_per_word_samples), 3
            ) if len(tokens_per_word_samples) > 1 else 0.0,
            "mean_tokens_per_char": round(statistics.mean(tokens_per_char_samples), 4),
            "chars_per_word": round(total_chars / total_words, 2) if total_words else 0.0,
            "total_tokens": total_tokens,
            "total_words": total_words,
            "total_chars": total_chars,
            "num_sentences_analyzed": len(tokens_per_word_samples),
            "sample_sentence": sample_sentence,
            "sample_token_breakdown": sample_token_strs,
        }

    baseline = results.get(config.BASELINE_LANGUAGE)
    if baseline:
        baseline_tpw = baseline["mean_tokens_per_word"]
        for label, stats in results.items():
            stats["ratio_vs_baseline"] = round(stats["mean_tokens_per_word"] / baseline_tpw, 3)

    return results


def run():
    corpus_data = load_corpus()
    print(f"Loaded corpus (fallback_corpus={corpus_data.get('fallback_corpus')})")

    from transformers import AutoTokenizer
    print(f"Loading tokenizer for {config.MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)

    results = analyze_tokenizer(tokenizer, corpus_data)

    print("\nTokenization efficiency (mean tokens/word, chars/word):")
    print(f"{'Language':12s} {'tok/word':>10s} {'vs ' + config.BASELINE_LANGUAGE:>12s} {'chars/word':>12s}")
    for label, stats in results.items():
        print(f"{label:12s} {stats['mean_tokens_per_word']:>10.3f} "
              f"{stats.get('ratio_vs_baseline', 1.0):>11.2f}x {stats['chars_per_word']:>12.1f}")

    output = {
        "model": config.MODEL_NAME,
        "fallback_corpus": corpus_data.get("fallback_corpus", False),
        "baseline_language": config.BASELINE_LANGUAGE,
        "per_language": results,
    }

    out_path = os.path.join(config.RESULTS_DIR, "tokenizer_analysis.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nWrote tokenizer analysis to {out_path}")
    return output


if __name__ == "__main__":
    run()