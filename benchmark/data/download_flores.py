"""
Pulls FLORES-200 (via the `facebook/flores` "all" config, which returns every
language as parallel columns for the same underlying sentence) and writes out
a JSON file of aligned sentences for just the languages this project cares about.

"Aligned" is the whole point: row N in English and row N in Hindi are
translations of the exact same sentence. That's what makes the tokens-per-word
comparison downstream a fair one — we're never comparing different content,
only how differently the same content gets tokenized.

Run directly to test in isolation:
    python data/download_flores.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# A small, hand-written fallback so the pipeline still runs end-to-end (with
# an honest, visible warning) if the Hub is unreachable or the dataset's
# column-naming convention has changed since this script was written.
# This is NOT a substitute for the real corpus — anything produced from this
# fallback gets clearly tagged in the results JSON so it can never be mistaken
# for a real benchmark number.
FALLBACK_CORPUS = {
    "English": [
        "The central bank raised interest rates again this quarter.",
        "She walked to the market to buy fresh vegetables.",
        "The new policy will take effect from the first of next month.",
        "Scientists discovered a new species of frog in the rainforest.",
        "He forgot his umbrella, so he got soaked in the rain.",
    ],
    "Hindi": [
        "केंद्रीय बैंक ने इस तिमाही में फिर से ब्याज दरें बढ़ा दीं।",
        "वह ताज़ी सब्जियाँ खरीदने के लिए बाज़ार गई।",
        "नई नीति अगले महीने की पहली तारीख से लागू होगी।",
        "वैज्ञानिकों ने वर्षावन में मेंढक की एक नई प्रजाति की खोज की।",
        "वह अपना छाता भूल गया, इसलिए बारिश में भीग गया।",
    ],
    "Tamil": [
        "மத்திய வங்கி இந்த காலாண்டில் மீண்டும் வட்டி விகிதங்களை உயர்த்தியது.",
        "அவள் புதிய காய்கறிகள் வாங்க சந்தைக்குச் சென்றாள்.",
        "புதிய கொள்கை அடுத்த மாதம் முதல் தேதியிலிருந்து நடைமுறைக்கு வரும்.",
        "மழைக்காடுகளில் விஞ்ஞானிகள் ஒரு புதிய தவளை இனத்தைக் கண்டுபிடித்தனர்.",
        "அவன் தனது குடையை மறந்துவிட்டான், அதனால் மழையில் நனைந்தான்.",
    ],
    "Bengali": [
        "কেন্দ্রীয় ব্যাংক এই প্রান্তিকে আবার সুদের হার বাড়িয়েছে।",
        "সে বাজারে গিয়েছিল তাজা সবজি কিনতে।",
        "নতুন নীতি আগামী মাসের প্রথম তারিখ থেকে কার্যকর হবে।",
        "বিজ্ঞানীরা রেইনফরেস্টে একটি নতুন প্রজাতির ব্যাঙ আবিষ্কার করেছেন।",
        "সে তার ছাতা ভুলে গিয়েছিল, তাই বৃষ্টিতে ভিজে গেল।",
    ],
    "Marathi": [
        "मध्यवर्ती बँकेने या तिमाहीत पुन्हा व्याजदर वाढवले.",
        "ती ताज्या भाज्या विकत घेण्यासाठी बाजारात गेली.",
        "नवीन धोरण पुढील महिन्याच्या पहिल्या तारखेपासून लागू होईल.",
        "शास्त्रज्ञांना पर्जन्यवनात बेडकाची एक नवीन प्रजाती सापडली.",
        "तो आपली छत्री विसरला, त्यामुळे तो पावसात भिजला.",
    ],
}


def _find_column(columns, lang_code):
    """
    FLORES's 'all' config names columns like 'sentence_eng_Latn'. Search
    rather than hard-code the exact prefix, so a minor naming change upstream
    doesn't silently break this script — it'll raise a clear error instead.
    """
    candidates = [c for c in columns if lang_code.lower() in c.lower()]
    if not candidates:
        return None
    # Prefer a column that actually starts with "sentence" if multiple match
    sentence_cols = [c for c in candidates if "sentence" in c.lower()]
    return sentence_cols[0] if sentence_cols else candidates[0]


def download_flores(num_sentences=None):
    """
    Returns dict: {language_label: [sentence, sentence, ...]}, aligned by index
    across all languages. Also writes the result to config.PARALLEL_CORPUS_PATH.
    """
    num_sentences = num_sentences or config.NUM_SENTENCES
    result = {}
    used_fallback = False

    try:
        from datasets import load_dataset

        print(f"Loading {config.FLORES_DATASET} (config='{config.FLORES_CONFIG}', "
              f"split='{config.FLORES_SPLIT}') from the Hub...")
        ds = load_dataset(config.FLORES_DATASET, config.FLORES_CONFIG, split=config.FLORES_SPLIT)
        columns = ds.column_names

        for label, lang_code in config.LANGUAGES.items():
            col = _find_column(columns, lang_code)
            if col is None:
                raise ValueError(
                    f"Could not find a column for language code '{lang_code}' "
                    f"(label '{label}') in FLORES columns: {columns[:20]}..."
                )
            sentences = ds[col][:num_sentences]
            result[label] = [s.strip() for s in sentences if s and s.strip()]
            print(f"  {label:10s} -> column '{col}', {len(result[label])} sentences")

        # Sanity check: every language should have the same sentence count
        # since they're parallel — if not, something upstream is misaligned.
        lengths = {label: len(sents) for label, sents in result.items()}
        if len(set(lengths.values())) > 1:
            print(f"WARNING: language sentence counts are not aligned: {lengths}")

    except Exception as e:
        print(f"FLORES download failed ({type(e).__name__}: {e}).")
        print("Falling back to the small built-in 5-sentence corpus.")
        print("Results derived from this run will be tagged 'fallback_corpus: true' "
              "in the output JSON — do NOT report these as your real benchmark numbers.")
        result = FALLBACK_CORPUS
        used_fallback = True

    output = {
        "languages": result,
        "fallback_corpus": used_fallback,
        "num_sentences_per_language": {label: len(s) for label, s in result.items()},
    }

    with open(config.PARALLEL_CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Wrote parallel corpus to {config.PARALLEL_CORPUS_PATH} "
          f"(fallback_corpus={used_fallback})")
    return output


if __name__ == "__main__":
    download_flores()
