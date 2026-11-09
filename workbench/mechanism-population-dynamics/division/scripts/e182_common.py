"""E182 shared definitions (card: division/experiments/E182-script-cost-lexical-carrier.md)."""
import unicodedata

FLORES = "/home/xiang/mechpop_cache/flores200/flores200_dataset"
TRANSLIT = {"srp_Latn": "/home/xiang/mechpop_cache/e180/srp_Latn",   # E180 Gaj transliterator output
            "uzn_Cyrl": "/home/xiang/mechpop_cache/e182/uzn_Cyrl"}   # e182_translit_uz.py output
GROUPS = {"S": ["srp_Cyrl", "srp_Latn", "mkd_Cyrl", "bul_Cyrl", "rus_Cyrl", "ukr_Cyrl",
                "hrv_Latn", "slv_Latn", "ces_Latn", "pol_Latn"],
          "U": ["uzn_Latn", "uzn_Cyrl", "kaz_Cyrl", "kir_Cyrl", "tur_Latn", "azj_Latn"],
          "H": ["hin_Deva", "urd_Arab", "npi_Deva", "mar_Deva", "snd_Arab", "pes_Arab"]}
LANGS = [x for g in GROUPS.values() for x in g]
MODELS = {"qwen3": ("Qwen/Qwen3-30B-A3B", "sdpa"),
          "qwen3base": ("Qwen/Qwen3-30B-A3B-Base", "sdpa"),
          "gptoss": ("openai/gpt-oss-20b", "eager"),
          "olmoe": ("allenai/OLMoE-1B-7B-0125-Instruct", "sdpa")}
# count classes stored by the capture: 0 ALL (E180-style, every token) | 1 LET | 2 NON | 3 NON-tm (type-matched)
CLASSES = ["ALL", "LET", "NON", "NONtm"]
APOS = set("'ʻʼ‘’`")


def token_class(s):
    """'let' = decoded token has a Unicode letter or mark (L*/M*); 'non' = non-empty, no letter/mark, no U+FFFD,
    no apostrophe-like char; 'frag' = contains U+FFFD (partial UTF-8 byte sequence); 'apos' = letterless but
    contains an apostrophe-like char (word-internal in Uzbek oʻ/gʻ/tutuq and Turkish suffixes); 'empty'."""
    if s == "":
        return "empty"
    if "�" in s:
        return "frag"
    if any(unicodedata.category(c)[0] in "LM" for c in s):
        return "let"
    if any(c in APOS for c in s):
        return "apos"
    return "non"


def read(split, lang, n=None):
    path = f"{TRANSLIT[lang]}/{split}/{lang}.{split}" if lang in TRANSLIT else f"{FLORES}/{split}/{lang}.{split}"
    with open(path, encoding="utf-8") as f:
        xs = [x.rstrip("\n") for x in f]
    return xs[:n] if n else xs
