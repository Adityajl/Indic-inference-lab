"""
Pulls FLORES+ (via openlanguagedata/flores_plus, the maintained Parquet-native
successor to facebook/flores) and writes out a JSON file of aligned sentences
for just the languages this project cares about.

Each language is loaded as its own per-language config (e.g. "hin_Deva").
Rows across languages share an `id` field when they're translations of the
same underlying sentence — so alignment means taking the intersection of ids
present in every language, then reading off the same ids in the same order
for each one. That's what makes the tokens-per-word comparison downstream
fair: every language is describing the exact same content.

Run directly to test in isolation:
    python data/download_flores.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


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


def download_flores(num_sentences=None):
    """
    Returns dict: {language_label: [sentence, sentence, ...]}, aligned by
    shared FLORES `id` across all languages. Also writes the result to
    config.PARALLEL_CORPUS_PATH.
    """
    num_sentences = num_sentences or config.NUM_SENTENCES
    result = {}
    used_fallback = False

    try:
        from datasets import load_dataset

        # Load each language as its own per-language config, then align by id.
        per_language_by_id = {}
        for label, lang_code in config.LANGUAGES.items():
            print(f"Loading {config.FLORES_DATASET} config='{lang_code}' "
                  f"split='{config.FLORES_SPLIT}'...")
            ds = load_dataset(config.FLORES_DATASET, lang_code, split=config.FLORES_SPLIT)
            id_to_text = {str(row["id"]): row["text"].strip() for row in ds if row.get("text")}
            per_language_by_id[label] = id_to_text
            print(f"  {label:10s} -> {len(id_to_text)} sentences")

        # Alignment: only keep ids present in EVERY language, so every row we
        # use really is a translation of the same sentence in all of them.
        common_ids = set.intersection(*(set(d.keys()) for d in per_language_by_id.values()))
        sorted_ids = sorted(common_ids, key=lambda x: int(x))[:num_sentences]

        if not sorted_ids:
            raise ValueError("No common sentence ids found across all configured languages.")

        for label, id_to_text in per_language_by_id.items():
            result[label] = [id_to_text[i] for i in sorted_ids if i in id_to_text]

        print(f"Aligned {len(sorted_ids)} common sentences across "
              f"{len(config.LANGUAGES)} languages.")

    except Exception as e:
        print(f"FLORES+ download failed ({type(e).__name__}: {e}).")
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