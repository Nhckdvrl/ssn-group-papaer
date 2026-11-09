#!/usr/bin/env python3
"""E180 Serbian Cyrillic -> Latin (Gaj) transliterator + round-trip check
(card: division/experiments/E180-script-vs-language-routing.md).

Usage: e180_translit.py [OUT_DIR]   writes OUT_DIR/{dev,devtest}/srp_Latn.{split} and prints the round-trip report.
"""
import json, os, re, sys, unicodedata

FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
LOW = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ђ": "đ", "е": "e", "ж": "ž", "з": "z", "и": "i",
       "ј": "j", "к": "k", "л": "l", "љ": "lj", "м": "m", "н": "n", "њ": "nj", "о": "o", "п": "p", "р": "r",
       "с": "s", "т": "t", "ћ": "ć", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "č", "џ": "dž", "ш": "š"}
UP = {k.upper(): v.capitalize() for k, v in LOW.items()}  # Љ -> Lj (title); all-caps handled below
CYR = set(LOW) | set(UP)


def cyr2lat(s):
    out = []
    for i, ch in enumerate(s):
        if ch in LOW:
            out.append(LOW[ch])
        elif ch in UP:
            v = UP[ch]
            if len(v) == 2:
                nxt = s[i + 1] if i + 1 < len(s) else ""
                prv = s[i - 1] if i > 0 else ""
                if nxt.isupper() or (prv.isupper() and not nxt.islower()):
                    v = v.upper()
            out.append(v)
        else:
            out.append(ch)
    return "".join(out)


INV = {}
for k, v in LOW.items():
    INV[v] = k
    INV[v.capitalize()] = k.upper()
    INV[v.upper()] = k.upper()
DIG = sorted([x for x in INV if len(x) == 2], key=len, reverse=True)


def lat2cyr(s):
    out, i = [], 0
    while i < len(s):
        two = s[i:i + 2]
        if two in INV and len(two) == 2:
            out.append(INV[two]); i += 2
        elif s[i] in INV:
            out.append(INV[s[i]]); i += 1
        else:
            out.append(s[i]); i += 1
    return "".join(out)


def read(split, lang):
    with open(f"{FLORES}/{split}/{lang}.{split}", encoding="utf-8") as f:
        return [x.rstrip("\n") for x in f]


def roundtrip_report(lines):
    words = [w for ln in lines for w in re.findall(r"\w+", ln)]
    cyr_words = [w for w in words if all(c in CYR for c in w)]
    bad = [w for w in cyr_words if lat2cyr(cyr2lat(w)) != w]
    latin_words = [w for w in words if any("LATIN" in unicodedata.name(c, "") for c in w)]
    mixed = [w for w in words if any(c in CYR for c in w) and any("LATIN" in unicodedata.name(c, "") for c in w)]
    leftover_cyr = sum(1 for ln in lines for c in cyr2lat(ln) if "CYRILLIC" in unicodedata.name(c, ""))
    return {"n_words": len(words), "n_cyrillic_words": len(cyr_words), "roundtrip_exact": 1 - len(bad) / max(len(cyr_words), 1),
            "roundtrip_failures": sorted(set(bad))[:50], "n_latin_words_kept": len(latin_words),
            "latin_words_examples": sorted(set(latin_words))[:40], "n_mixed_script_words": len(mixed),
            "cyrillic_chars_left_after_translit": leftover_cyr}


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    rep = {}
    for split in ("dev", "devtest"):
        src = read(split, "srp_Cyrl")
        rep[split] = roundtrip_report(src)
        if out:
            os.makedirs(os.path.join(out, split), exist_ok=True)
            with open(os.path.join(out, split, f"srp_Latn.{split}"), "w", encoding="utf-8") as f:
                f.write("\n".join(cyr2lat(x) for x in src) + "\n")
    # all-caps / title-case digraph unit tests
    tests = {"ЉУБЉАНА": "LJUBLJANA", "Љубљана": "Ljubljana", "Њујорк": "Njujork", "ЏЕП": "DŽEP", "Џеп": "Džep",
             "НЊ": "NNJ", "Љ": "Lj", "ђак": "đak", "ћуфта": "ćufta"}
    rep["unit_tests"] = {k: (cyr2lat(k), cyr2lat(k) == v, lat2cyr(cyr2lat(k)) == k) for k, v in tests.items()}
    print(json.dumps(rep, ensure_ascii=False, indent=1))
