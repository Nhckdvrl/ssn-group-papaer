"""L36 E00 Gate A — rebuild and freeze the ACL-2022 intrinsic-uncertainty substrate.

Reconstructs Stahlberg, Kulikov & Kumar (ACL 2022) eq. (1) on the official WMT19 English->German
test set (newstest2019) paired with the independently authored AR reference of Freitag et al.
(2020).  Writes the frozen u table, the quartile cut points and a sha256 manifest.

No model is loaded here, by design: u must exist before any generation.
"""

import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request

from rapidfuzz.distance import Levenshtein

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "raw")
OUT = os.path.join(ROOT, "results", "e00")

WMT19_TEST_URL = "https://data.statmt.org/wmt19/translation-task/test.tgz"
AR_REF_URL = ("https://raw.githubusercontent.com/google/wmt19-paraphrased-references/"
              "master/wmt19/ende/wmt19-ende-ar.ref")
WMT18_TEST_URL = "https://data.statmt.org/wmt18/translation-task/test.tgz"

SEG_RE = re.compile(r'<seg id="\d+">(.*)</seg>')


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url, path):
    if not os.path.exists(path):
        print(f"[fetch] {url}")
        urllib.request.urlretrieve(url, path)
    return path


def extract_sgm(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = SEG_RE.search(line.strip())
            if m:
                out.append(html.unescape(m.group(1)).strip())
    return out


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def u_char(a, b):
    return Levenshtein.distance(a, b) / ((len(a) + len(b)) / 2)


def u_word(a, b):
    A, B = a.split(), b.split()
    return Levenshtein.distance(A, B) / ((len(A) + len(B)) / 2)


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    # --- inputs -----------------------------------------------------------------------------
    test19 = fetch(WMT19_TEST_URL, os.path.join(RAW, "wmt19_test.tgz"))
    test18 = fetch(WMT18_TEST_URL, os.path.join(RAW, "wmt18_test.tgz"))
    ar = fetch(AR_REF_URL, os.path.join(RAW, "wmt19-ende-ar.ref"))

    with tarfile.open(test19) as tf:
        for name in ("sgm/newstest2019-ende-src.en.sgm", "sgm/newstest2019-ende-ref.de.sgm"):
            tf.extract(name, RAW)
    with tarfile.open(test18) as tf:
        names = [n for n in tf.getnames() if "newstest2018-ende" in n and n.endswith(".sgm")]
        for n in names:
            tf.extract(n, RAW)   # lands under RAW/test/ for the 2018 archive

    src = extract_sgm(os.path.join(RAW, "sgm/newstest2019-ende-src.en.sgm"))
    ref_wmt = extract_sgm(os.path.join(RAW, "sgm/newstest2019-ende-ref.de.sgm"))
    ref_ar = [l.rstrip("\n") for l in open(ar, encoding="utf-8")]

    assert len(src) == len(ref_wmt) == len(ref_ar) == 1997, (len(src), len(ref_wmt), len(ref_ar))

    write_lines(os.path.join(DATA, "newstest2019.en"), src)
    write_lines(os.path.join(DATA, "newstest2019.wmtref.de"), ref_wmt)
    write_lines(os.path.join(DATA, "newstest2019.arref.de"), ref_ar)

    # substrate-blind model-screening set (Gate C): a *different year*
    src18 = extract_sgm(os.path.join(RAW, "test", "newstest2018-ende-src.en.sgm"))
    ref18 = extract_sgm(os.path.join(RAW, "test", "newstest2018-ende-ref.de.sgm"))
    assert len(src18) == len(ref18)
    write_lines(os.path.join(DATA, "newstest2018.en"), src18)
    write_lines(os.path.join(DATA, "newstest2018.ref.de"), ref18)

    # --- uncertainty (ACL-2022 eq. 1, n=2) ---------------------------------------------------
    rows = []
    for i, (s, a, b) in enumerate(zip(src, ref_wmt, ref_ar)):
        rows.append({
            "idx": i,
            "src_words": len(s.split()),
            "ref_words": len(a.split()),
            "u_char": u_char(a, b),
            "u_word": u_word(a, b),
        })

    uc = sorted(r["u_char"] for r in rows)

    def q(p):
        return uc[int(round(p * (len(uc) - 1)))]

    cuts = {"q25": q(0.25), "q50": q(0.50), "q75": q(0.75)}
    for r in rows:
        v = r["u_char"]
        r["stratum"] = ("Q1" if v <= cuts["q25"] else
                        "Q2" if v <= cuts["q50"] else
                        "Q3" if v <= cuts["q75"] else "Q4")

    with open(os.path.join(DATA, "uncertainty.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # --- Gate A.3 agreement check ------------------------------------------------------------
    import numpy as np
    from scipy.stats import spearmanr

    a_c = np.array([r["u_char"] for r in rows])
    a_w = np.array([r["u_word"] for r in rows])
    rho = float(spearmanr(a_c, a_w).statistic)

    def quartile_labels(vals):
        order = np.argsort(np.argsort(vals))
        return (order / len(vals) * 4).astype(int).clip(0, 3)

    same = float((quartile_labels(a_c) == quartile_labels(a_w)).mean())

    lens = np.array([r["ref_words"] for r in rows])
    buckets = {}
    for lo, hi, name in [(0, 10, "[0,10]"), (10, 20, "(10,20]"), (20, 30, "(20,30]"),
                         (30, 10 ** 9, "(30,)")]:
        m = (lens > lo) & (lens <= hi) if lo else (lens <= hi)
        buckets[name] = {"n": int(m.sum()), "u_char": float(a_c[m].mean()),
                         "u_word": float(a_w[m].mean())}

    manifest = {
        "gate": "A",
        "built_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                    capture_output=True, text=True).stdout.strip(),
        "definition": "u = d_edit(y_wmt, y_ar) / ((|y_wmt| + |y_ar|) / 2)  [ACL 2022 eq. 1, n=2]",
        "primary_unit": "character",
        "n_segments": len(rows),
        "inputs": {
            "wmt19_test.tgz": {"url": WMT19_TEST_URL, "sha256": sha256(test19)},
            "wmt18_test.tgz": {"url": WMT18_TEST_URL, "sha256": sha256(test18)},
            "wmt19-ende-ar.ref": {"url": AR_REF_URL, "sha256": sha256(ar)},
        },
        "derived": {
            name: sha256(os.path.join(DATA, name)) for name in
            ["newstest2019.en", "newstest2019.wmtref.de", "newstest2019.arref.de",
             "newstest2018.en", "newstest2018.ref.de", "uncertainty.jsonl"]
        },
        "u_char": {"mean": float(a_c.mean()), "median": float(np.median(a_c)),
                   "min": float(a_c.min()), "max": float(a_c.max())},
        "u_word": {"mean": float(a_w.mean()), "median": float(np.median(a_w))},
        "quartile_cuts_u_char": cuts,
        "stratum_sizes": {k: sum(1 for r in rows if r["stratum"] == k)
                          for k in ["Q1", "Q2", "Q3", "Q4"]},
        "length_profile": buckets,
        "gate_A3_unit_agreement": {"spearman_rho": rho, "same_quartile_frac": same,
                                   "threshold_rho": 0.90, "threshold_same_quartile": 0.80,
                                   "pass": bool(rho >= 0.90 and same >= 0.80)},
    }
    with open(os.path.join(OUT, "substrate_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(json.dumps({k: manifest[k] for k in
                      ["n_segments", "u_char", "u_word", "quartile_cuts_u_char",
                       "stratum_sizes", "length_profile", "gate_A3_unit_agreement"]}, indent=2))
    print("GATE A:", "PASS" if manifest["gate_A3_unit_agreement"]["pass"] else "FAIL")
    return 0 if manifest["gate_A3_unit_agreement"]["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
