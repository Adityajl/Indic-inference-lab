# Indic Inference Lab

**A model with no official Indic-language support needs up to 7.6× more tokens to say the same sentence in Tamil as in English — and INT8 quantization makes inference ~4.5× *slower*, not faster, at single-request batch size.**

🔗 **Live dashboard:** https://indic-inference-lab.vercel.app/ · 📊 **Benchmark code:** [`/benchmark`](./benchmark) · 🖥️ **Dashboard code:** [`/dashboard`](./dashboard)

---

## The problem, precisely stated

Public LLM inference benchmarks are run almost exclusively on English text. Tokenizers trained predominantly on English/Latin-script data fragment non-Latin scripts — Hindi (Devanagari), Tamil, Bengali, Marathi — into far more subword tokens per word than they do English. More tokens per word means, for the *exact same sentence*: higher latency, higher per-request cost (API pricing is per-token), and less usable context window.

This project measures that gap precisely, using **Qwen2.5-1.5B-Instruct** — a model whose officially documented language list does **not** include Hindi, Tamil, Bengali, or Marathi. That's a deliberate framing choice: the finding here is *"a model without official Indic support shows this gap,"* not a categorical claim about all LLMs. A natural extension (see [What I'd do next](#what-id-do-with-more-time)) is testing a model that *does* claim Indic support, to see whether the gap shrinks.

## Key findings

### 1. Tokenization cost, measured on parallel content — not estimated

Every language below is measured on the *same underlying sentences*, via [FLORES+](https://huggingface.co/datasets/openlanguagedata/flores_plus) (devtest split, 200 aligned sentences) — so any gap is attributable to tokenization, not to languages saying different amounts of "stuff."

| Language | tok/word ratio | tok/char ratio | chars/word |
|---|---|---|---|
| English (baseline) | 1.00× | 1.00× | 6.1 |
| Hindi | 3.65× | 4.30× | 5.1 |
| Marathi | 5.14× | 4.43× | 7.0 |
| Bengali | 5.53× | 4.97× | 6.8 |
| Tamil | **7.58×** | 5.05× | 9.1 |

**The insight that matters more than any single number:** look at how much *tighter* the character-level column is (4.30×–5.05×) compared to the word-level column (3.65×–7.58×). Tamil's word-level ratio looks like a dramatic outlier — almost double Hindi's — but per character, Tamil and Hindi are both just "the tokenizer is ~4.3–5x worse at this script than English," nearly identically. The rest of Tamil's apparent gap is explained by its own `chars/word` column: Tamil is agglutinative, so grammatical particles fuse onto root words without spaces, making whitespace-delimited "words" inherently longer — *independent of tokenizer quality*. Reporting only the word-level ratio, as most quantization/tokenization writeups do, would have overstated Tamil's specific problem and obscured that all four Indic scripts are failed by this tokenizer at roughly the same character-level rate.

### 2. INT8 quantization made inference slower, not faster — and that's the correct, expected result

| | FP16 mean latency | INT8 mean latency | Result |
|---|---|---|---|
| English | 2.62s | 11.70s | 4.46× slower |
| Hindi | 2.63s | 11.83s | 4.50× slower |
| Tamil | 2.64s | 11.60s | 4.39× slower |
| Bengali | 2.63s | 11.94s | 4.55× slower |
| Marathi | 2.65s | 11.79s | 4.46× slower |

Same hardware (Tesla T4), same 30 prompts per language, same generation length, batch size 1 — only the quantization changes between runs. The ratio holds within **4.39×–4.55×** across every language, and that tightness is the actual evidence this is real: a systematic effect produces consistent ratios across unrelated conditions, noise doesn't.

**Why this is correct, not a bug:** `bitsandbytes`'s `load_in_8bit` (LLM.int8()) is a *memory*-reduction technique, not a *latency*-reduction one. It dequantizes INT8 weights back to floating point on every forward pass — overhead that dominates at batch size 1 on a Turing-architecture GPU (T4) that lacks the efficient native INT8 tensor-core paths newer Ampere+ GPUs have. Most public benchmarks report quantization speedups measured at large batch sizes on modern hardware; this result is what happens at the opposite end of that spectrum, and it's a more useful, more honest finding than confirming the obvious.

### 3. Real cost impact, per request

For a typical 50-word request, same content, same model:

| Language | Estimated tokens needed |
|---|---|
| English | 65.6 |
| Hindi | 239.8 |
| Marathi | 337.4 |
| Bengali | 363.1 |
| Tamil | 497.4 |

At any per-token API pricing, this translates directly into proportional cost — Tamil users would pay roughly 7.6× more than English users for equivalent requests, before quantization is even considered.

## Architecture (and why it's split this way)

```
                    ┌─────────────────────────┐
                    │   benchmark/  (Python)   │
                    │   Runs on a GPU          │
                    │   (free Colab T4 works)  │
                    │                          │
                    │  1. Pull FLORES+ corpus  │
                    │  2. Tokenizer analysis   │
                    │  3. Load model FP16      │
                    │  4. Quantize to INT8     │
                    │  5. Benchmark both       │
                    │  6. Write results JSON   │
                    └────────────┬─────────────┘
                                 │ benchmark_results.json
                                 ▼
                    ┌─────────────────────────┐
                    │   dashboard/ (Next.js)   │
                    │   Deployed on Vercel     │
                    │                          │
                    │  Reads the JSON, renders │
                    │  it. No model, no GPU,   │
                    │  no backend here.        │
                    └─────────────────────────┘
```

Vercel's serverless functions have no GPU access, so the heavy compute (quantized inference) runs separately from the presentation layer — the same separation production ML systems use between inference clusters and dashboards, applied here deliberately rather than as a workaround.

## Repo structure

```
indic-inference-lab/
├── benchmark/
│   ├── requirements.txt
│   ├── config.py                   # every tunable parameter lives here
│   ├── data/download_flores.py     # pulls + aligns the FLORES+ corpus
│   ├── tokenizer_analysis.py       # tokens/word, tokens/char, chars/word per language
│   ├── quantize_and_benchmark.py   # FP16 vs INT8 latency/throughput
│   ├── run_all.py                  # orchestrates the full pipeline
│   └── results/benchmark_results.json
├── dashboard/
│   ├── app/page.tsx                # assembles every section
│   ├── components/
│   │   ├── TokenBreakdownHero.tsx        # interactive language switcher
│   │   ├── WordVsCharComparison.tsx       # the word/char nuance, made visible
│   │   ├── QuantizationSpeedupCards.tsx   # the INT8 finding
│   │   ├── CostProjectionSection.tsx
│   │   └── MethodologyFooter.tsx
│   └── data/
│       ├── benchmark_results.json   # real results, committed
│       └── sample_results.json      # placeholder, clearly flagged in-UI
└── README.md
```

## Running it yourself

**Benchmark (needs a GPU — free Colab T4 is enough):**
```bash
cd benchmark
pip install -r requirements.txt
python run_all.py
```
FLORES+ is a gated dataset — accept its terms at [huggingface.co/datasets/openlanguagedata/flores_plus](https://huggingface.co/datasets/openlanguagedata/flores_plus) and authenticate with `huggingface_hub.login()` before running.

**Dashboard:**
```bash
cd dashboard
npm install
npm run dev
```
To deploy: push to GitHub, import into Vercel, and set **Root Directory to `dashboard`** — the single most common deploy mistake with this layout.

## Engineering notes — what actually went wrong, and why it's worth reading

A benchmark this size doesn't run clean on the first try, and the real debugging is as much a part of this project as the final numbers:

- **`facebook/flores` is deprecated.** As of `datasets` v4.0+, Hugging Face dropped support for "loading-script" datasets entirely. Migrated to `openlanguagedata/flores_plus`, the maintained Parquet-native successor — which turned out to be **gated**, requiring explicit consent + an HF token, not just a library swap.
- **`bitsandbytes` API drift.** `load_in_8bit=True` as a direct keyword argument to `from_pretrained()` was removed; current versions require an explicit `BitsAndBytesConfig` object.
- **Silent tokenizer decode bug.** Visualizing token boundaries by calling `tokenizer.decode()` on individual token IDs produced mojibake (`�`) for every Indic language — because Qwen's byte-level BPE tokenizer can split a single multi-byte UTF-8 character across multiple tokens, and decoding a byte-fragment alone is invalid UTF-8. Fixed by using `return_offsets_mapping` to slice the *original* string by token boundaries instead of decoding token IDs at all.
- **A genuine bundler-level rendering bug, correctly root-caused and then deliberately scoped around.** Two Recharts bar charts rendered an empty `<div>` with zero DOM nodes inside, with no console errors, on Next.js 16 + Turbopack. After isolating the cause (a `ResponsiveContainer` dimension-measurement timing issue, distinct from a known React 19 incompatibility that was ruled out by checking the actually-installed package versions, not just `package.json`), the pragmatic call was to drop the two broken bar charts entirely rather than chase a bundler-specific rendering quirk further, keeping every other section — including the project's most important finding, the word/char nuance table — fully intact and fully working.

## Limitations

- Single model (Qwen2.5-1.5B-Instruct), single GPU (Tesla T4), batch size 1 — results characterize *this* model on *this* hardware under *this* workload, not LLMs broadly.
- 200 sentences for tokenizer stats, 30 prompts per language for latency — sufficient for a clear, consistent signal here, but not a large-scale statistical study.
- Word-level tokenization metrics use whitespace splitting, valid for every language tested here (all use whitespace word boundaries) — would need a different segmentation approach for languages like Chinese or Japanese.

## What I'd do with more time

- Test a model that *does* claim Indic-language support (e.g. a Sarvam or Qwen3.5 variant) to see whether the gap shrinks, isolating "lack of training data" from "tokenizers are just hard for these scripts" as separate causes.
- Re-run the INT8 benchmark at larger batch sizes, where `bitsandbytes`'s memory savings might convert into a genuine *throughput* win even though single-request latency gets worse.
- Compare against AWQ/GPTQ quantization, which are designed for inference speed rather than `bitsandbytes`'s memory-focused approach.

## Stack

Python, PyTorch, Hugging Face `transformers`/`datasets`, `bitsandbytes` · Next.js 16 (App Router), TypeScript, Tailwind CSS · Tesla T4 (Colab), Vercel
