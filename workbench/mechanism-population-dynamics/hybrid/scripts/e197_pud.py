#!/usr/bin/env python3
"""Build E197's parallel corpus from UD PUD test treebanks (1000 sentences, aligned by sent_id).
Usage: e197_pud.py OUT_JSON  (downloads from github raw: UniversalDependencies/UD_<Lang>-PUD)"""
import json, sys, urllib.request
LANGS = {"en": "English", "fr": "French", "de": "German", "es": "Spanish", "ru": "Russian", "zh": "Chinese",
         "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "hi": "Hindi", "th": "Thai", "tr": "Turkish"}
data = {}
for code, name in LANGS.items():
    url = f"https://raw.githubusercontent.com/UniversalDependencies/UD_{name}-PUD/master/{code}_pud-ud-test.conllu"
    txt = urllib.request.urlopen(url, timeout=60).read().decode("utf-8")
    sid = None
    for line in txt.splitlines():
        if line.startswith("# sent_id = "):
            sid = line.split("= ", 1)[1].strip()
        elif line.startswith("# text = ") and sid:
            data.setdefault(sid, {})[code] = line.split("= ", 1)[1].strip()
            sid = None
ids = sorted(k for k, v in data.items() if len(v) == len(LANGS))
json.dump({"langs": list(LANGS), "ids": ids, "text": {k: data[k] for k in ids}}, open(sys.argv[1], "w"), ensure_ascii=False)
print(len(ids), "fully parallel sentences")
