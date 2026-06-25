"""
Measures tokenization efficiency per language on the aligned FLORES corpus.

Core metric: tokens-per-word. Since FLORES sentences are translations of the
exact same underlying content, any difference in tokens-per-word between
English and, say, Tamil is attributable to the tokenizer/script, not to the
languages saying different amounts of "stuff."

Word counts use whitespace splitting. This is valid for every language in
this project's default config (Hindi, Tamil, Bengali, Marathi, English all
use whitespace to separate words) — it would NOT be valid for a script like
Japanese or Chinese that doesn't use whitespace word boundaries. If you add
a language like that, swap in a proper word segmenter first.

Run directly to test in isolation (after running download_flores.py):
    python tokenizer_analysis.py
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
    """
    Returns a dict keyed by language label with per-language stats and a
    sample tokenization (for the dashboard's token-breakdown visualization).
    """
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

        # Build one illustrative token breakdown for the dashboard's hero
        # visual: pick a short-ish sentence so the rendered chunks stay legible.
        sample_sentence = min(sentences, key=lambda s: len(s.split())) if sentences else ""
        sample_token_ids = tokenizer.encode(sample_sentence, add_special_tokens=False)
        sample_token_strs = [tokenizer.decode([tid]) for tid in sample_token_ids]

        results[label] = {
            "mean_tokens_per_word": round(statistics.mean(tokens_per_word_samples), 3),
            "median_tokens_per_word": round(statistics.median(tokens_per_word_samples), 3),
            "stdev_tokens_per_word": round(
                statistics.stdev(tokens_per_word_samples), 3
            ) if len(tokens_per_word_samples) > 1 else 0.0,
            "mean_tokens_per_char": round(statistics.mean(tokens_per_char_samples), 4),
            "total_tokens": total_tokens,
            "total_words": total_words,
            "total_chars": total_chars,
            "num_sentences_analyzed": len(tokens_per_word_samples),
            "sample_sentence": sample_sentence,
            "sample_token_breakdown": sample_token_strs,
        }

    # Express everything relative to the baseline language too — this is the
    # "X times more tokens than English for the same content" number that
    # actually goes on a resume bullet or in an interview answer.
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

    print("\nTokenization efficiency (mean tokens/word):")
    print(f"{'Language':12s} {'tok/word':>10s} {'vs ' + config.BASELINE_LANGUAGE:>12s}")
    for label, stats in results.items():
        print(f"{label:12s} {stats['mean_tokens_per_word']:>10.3f} "
              f"{stats.get('ratio_vs_baseline', 1.0):>11.2f}x")

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
