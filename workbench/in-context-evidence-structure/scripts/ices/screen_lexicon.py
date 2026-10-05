"""Audit nonce-word candidates with step-5 (one judgment per word, batches of 10)."""
import asyncio, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ices.step5 import run_all, extract_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BATCH = 5
LIMIT = 200
PROMPT = """You are auditing candidate NONCE words for a psycholinguistics-style experiment on language models.
The words will be used as meaningless {role}. A word must be REJECTED if ANY of these holds:
 (a) it is a real word, common proper name, brand, abbreviation, or widespread internet slang in English or in any major language
     (Spanish, French, German, Italian, Portuguese, Dutch, Indonesian/Malay, Turkish, Swahili, Japanese romaji, Chinese pinyin with or without tones, Korean romanization, Hindi romanized, Russian transliterated);
 (b) it is a very common English word with one letter changed AND would likely be read as that word (e.g. 'blak' -> black);
 (c) it has an obvious meaning/sound-symbolic association with any BINARY concept: yes/no, on/off, true/false, good/bad, positive/negative, big/small, high/low, left/right, male/female, hot/cold, open/closed, win/lose, or with a number;
 (d) it resembles a vulgar, offensive or sensitive word.
Otherwise ACCEPT. Be careful and conservative; when you are genuinely unsure whether (a)-(d) holds, REJECT.

Words:
{words}

Return ONLY a JSON array with one object per word in the same order:
[{{"word": "...", "verdict": "accept" | "reject", "reason": "short reason (which criterion, which language/word)"}}]"""


def main():
    cand = json.loads((ROOT / "data" / "lexicon_candidates.json").read_text())
    jobs = []
    for role, key in (("feature names (like variable names) in a classification task", "attribute_names"),
                      ("category labels in a classification task", "labels")):
        ws = cand[key][:LIMIT]
        for i in range(0, len(ws), BATCH):
            batch = ws[i:i + BATCH]
            jobs.append((f"{key}:{i}", PROMPT.format(role=role, words="\n".join(batch))))
    out = asyncio.run(run_all(jobs, ROOT / "data" / "step5_lexicon_cache.jsonl", max_tokens=32000))
    verdicts = {}
    for pid, content in out.items():
        if not pid.endswith(tuple(f":{i}" for i in range(0, LIMIT, BATCH))):
            continue
        key, i = pid.split(":")
        batch = cand[key][int(i):int(i) + BATCH]
        try:
            arr = extract_json(content)
        except ValueError:
            arr = []
        byw = {d["word"].strip().lower(): d for d in arr}
        for w in batch:
            d = byw.get(w)
            verdicts.setdefault(key, {})[w] = d if d else {"word": w, "verdict": "reject", "reason": "missing"}
    res = {k: sorted(w for w, d in v.items() if d["verdict"] == "accept") for k, v in verdicts.items()}
    (ROOT / "data" / "lexicon_step5_verdicts.json").write_text(json.dumps(verdicts, indent=1))
    (ROOT / "data" / "lexicon.json").write_text(json.dumps(res, indent=1))
    for k, v in res.items():
        print(k, "accepted", len(v), "of", len(cand[k]))


if __name__ == "__main__":
    main()
