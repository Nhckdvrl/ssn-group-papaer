#!/usr/bin/env python3
"""E182 Uzbek Latin -> Cyrillic transliterator + round-trip check
(card: division/experiments/E182-script-cost-lexical-carrier.md).

Rules (modern Uzbek Latin -> Uzbek Cyrillic, 1995/2019 orthography):
  single letters  a а, b б, d д, f ф, g г, h ҳ, i и, j ж, k к, l л, m м, n н, o о, p п, q қ, r р, s с, t т,
                  u у, v в, x х, y й, z з; foreign c -> ц, w -> в
  digraphs        oʻ -> ў, gʻ -> ғ (any apostrophe variant ' ʻ ʼ ‘ ’ ` after o / g), sh -> ш, ch -> ч,
                  yo -> ё, yu -> ю, ya -> я
  e / ye          (ambiguous rule 1) word-initial or after a vowel: "ye" -> е, "e" -> э;
                  after a consonant: "e" -> е, "ye" -> йе
  apostrophe      (ambiguous rule 2) apostrophe not after o/g and between two letters -> ъ (tutuq belgisi);
                  otherwise left as is (punctuation)
  not recoverable (documented, left as written): Russian loans' ц written "s"/"ts" in Latin (kept с / тс),
                  ь / ъ dropped in Latin loans, "ng" -> нг (n + g, which is also the Cyrillic spelling)
  case            Cyrillic letter is upper iff the first Latin character of the (di)graph is upper.
Round trip: Cyrillic -> Latin with the inverse rules (ў -> o', ғ -> g', ъ -> ', е -> ye word-initially / after a
vowel / after ъ, else e; э -> e; ц -> c); compared with the original after normalising apostrophe variants to '.

Usage: e182_translit_uz.py [OUT_DIR]   writes OUT_DIR/{dev,devtest}/uzn_Cyrl.{split}; prints the report (JSON).
"""
import collections, json, os, re, sys, unicodedata

FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
APOS = set("'ʻʼ‘’`")
SINGLE = {"a": "а", "b": "б", "d": "д", "f": "ф", "g": "г", "h": "ҳ", "i": "и", "j": "ж", "k": "к", "l": "л",
          "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у", "v": "в",
          "x": "х", "y": "й", "z": "з", "c": "ц", "w": "в"}
DIG = {"sh": "ш", "ch": "ч", "yo": "ё", "yu": "ю", "ya": "я"}
VOW_L = set("aeiouAEIOU")
VOW_C = set("аеёиоуўэюяАЕЁИОУЎЭЮЯ")


def isletter(c):
    return c != "" and unicodedata.category(c)[0] in "LM"


def lat2cyr(s, stats=None):
    out, i, n = [], 0, len(s)
    st = stats if stats is not None else collections.Counter()
    while i < n:
        c = s[i]
        lc = c.lower()
        up = c.isupper()
        prev = s[i - 1] if i > 0 else ""
        word_start = not (isletter(prev) or prev in APOS)
        after_vowel = prev in VOW_L
        nxt = s[i + 1] if i + 1 < n else ""
        cy = None
        if lc in "og" and nxt in APOS:
            cy, step = ("ў" if lc == "o" else "ғ"), 2
        elif lc == "y" and nxt.lower() == "e":
            if word_start or after_vowel:
                cy, step = "е", 2
                st["ye_initial_or_after_vowel"] += 1
            else:
                cy, step = "йе", 2
                st["ye_after_consonant"] += 1
        elif (lc + nxt.lower()) in DIG:
            cy, step = DIG[lc + nxt.lower()], 2
        elif lc == "e":
            if word_start or after_vowel:
                cy, step = "э", 1
                st["e_initial_or_after_vowel"] += 1
            else:
                cy, step = "е", 1
        elif lc in SINGLE and c.isascii():
            cy, step = SINGLE[lc], 1
            if lc in "cw":
                st["foreign_" + lc] += 1
            if lc == "t" and nxt.lower() == "s":
                st["ts_kept"] += 1
        elif c in APOS:
            if isletter(prev) and isletter(nxt):
                cy, step = "ъ", 1
                st["apostrophe_to_hard_sign"] += 1
            else:
                out.append(c); i += 1
                st["apostrophe_kept_punct"] += 1
                continue
        else:
            if isletter(c) and "LATIN" in unicodedata.name(c, ""):
                st["other_latin_kept"] += 1
            out.append(c); i += 1
            continue
        if up:
            cy = cy[0].upper() + cy[1:]
        out.append(cy)
        i += step
    return "".join(out)


INV = {v: k for k, v in SINGLE.items() if k not in "cw"}
INV.update({"ц": "c", "ш": "sh", "ч": "ch", "ё": "yo", "ю": "yu", "я": "ya", "ў": "o'", "ғ": "g'", "ъ": "'",
            "э": "e"})


def cyr2lat(s):
    out = []
    for i, c in enumerate(s):
        lc = c.lower()
        up = c.isupper()
        prev = s[i - 1] if i > 0 else ""
        if lc == "е":
            v = "ye" if (not isletter(prev) or prev in VOW_C or prev in "ъЪ") else "e"
        elif lc in INV:
            v = INV[lc]
        else:
            out.append(c)
            continue
        if up:
            nxt = s[i + 1] if i + 1 < len(s) else ""
            allcaps = nxt.isupper() or (prev.isupper() and not nxt.islower())
            v = v.upper() if allcaps else v[0].upper() + v[1:]
        out.append(v)
    return "".join(out)


def norm_apos(s):
    return "".join("'" if c in APOS else c for c in s)


def read(split, lang):
    with open(f"{FLORES}/{split}/{lang}.{split}", encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f]


WORD = re.compile(r"[^\W\d_]+(?:['ʻʼ‘’`][^\W\d_]+)*")


def report(lines):
    st = collections.Counter()
    conv = [lat2cyr(x, st) for x in lines]
    words = [w for ln in lines for w in WORD.findall(ln)]
    lat_words = [w for w in words if all(c.isascii() or c in APOS for c in w)]
    bad = [w for w in lat_words if cyr2lat(lat2cyr(w)) != norm_apos(w)]
    line_rt = sum(cyr2lat(c) == norm_apos(x) for x, c in zip(lines, conv)) / len(lines)
    left_latin = sum(1 for ln in conv for c in ln if isletter(c) and "LATIN" in unicodedata.name(c, ""))
    return {"n_lines": len(lines), "n_words": len(words), "n_ascii_latin_words": len(lat_words),
            "roundtrip_exact_words": 1 - len(bad) / max(len(lat_words), 1), "roundtrip_failures": sorted(set(bad))[:50],
            "roundtrip_exact_lines": line_rt, "latin_letters_left_after_translit": left_latin,
            "rule_counts": dict(st)}, conv


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    rep = {}
    for split in ("dev", "devtest"):
        src = read(split, "uzn_Latn")
        rep[split], conv = report(src)
        if out:
            os.makedirs(os.path.join(out, split), exist_ok=True)
            with open(os.path.join(out, split, f"uzn_Cyrl.{split}"), "w", encoding="utf-8") as f:
                f.write("\n".join(conv) + "\n")
        rep[split]["examples"] = [(src[k], conv[k]) for k in (0, 1, 2)]
    tests = {"o'zbek": "ўзбек", "O'zbekiston": "Ўзбекистон", "g'alaba": "ғалаба", "shahar": "шаҳар",
             "choy": "чой", "yoz": "ёз", "dunyo": "дунё", "yaxshi": "яхши", "yuz": "юз", "yer": "ер", "eshik": "эшик",
             "poema": "поэма", "kecha": "кеча", "ma'no": "маъно", "SHAHAR": "ШАҲАР", "Ehud": "Эҳуд", "obyekt": "обйект",
             "bo'lishi": "бўлиши", "qo'shib": "қўшиб", "boshlang'ich": "бошланғич", "Shotlandiya": "Шотландия"}
    rep["unit_tests"] = {k: (lat2cyr(k), lat2cyr(k) == v, cyr2lat(lat2cyr(k)) == norm_apos(k)) for k, v in tests.items()}
    rep["unit_tests_all_pass"] = all(a and b for _, a, b in rep["unit_tests"].values())
    print(json.dumps(rep, ensure_ascii=False, indent=1))
