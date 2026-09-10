"""Score raw runs into a condition-level table.

SQuAD-v2 note: the parent reports lm-eval's `best_exact`, which sweeps a
no-answer threshold and therefore can never fall below the fraction of
unanswerable questions in the split (SQuAD-v2 dev: 5945/11873 = 50.07%).  We
report that quantity for comparability AND the artifact-free `HasAns_exact`,
which is exact match restricted to answerable questions.
"""
from __future__ import annotations
import json, pathlib, re, sys, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.tasks import squad_norm, gsm_extract

ROOT = pathlib.Path(__file__).resolve().parents[1]
NUM = re.compile(r"-?\d[\d,]*\.?\d*")
LETTER = re.compile(r"\b([ABCD])\b")
ANSLINE = re.compile(r"[Aa]nswer\s*(?:is)?\s*:?\s*\(?([ABCD])\)?")


def flex_num(t):
    m = NUM.findall(t.replace("$", ""))
    return m[-1].replace(",", "").rstrip(".") if m else None


def score(path):
    lines = [json.loads(l) for l in open(path)]
    meta, recs = lines[0], lines[1:]
    cell = meta["cell"]
    out = {**{k: v for k, v in meta.items() if k != "_meta"}}
    n = len(recs)

    correct = None
    if cell.endswith("_rank"):
        correct = [int(r["pred_index"] == r["gold_index"]) for r in recs]
        out["acc"] = sum(correct) / n

    elif cell.startswith("mmlu_gen"):
        correct, fmt = [], 0
        for r in recs:
            t = r["output"]
            m = ANSLINE.search(t) or LETTER.search(t.strip()[:40])
            fmt += m is not None
            correct.append(int(m is not None and m.group(1) == r["gold"]))
        out["acc"] = sum(correct) / n
        out["parse_rate"] = fmt / n
        out["mean_out_chars"] = sum(len(r["output"]) for r in recs) / n

    elif cell.startswith("gsm8k"):
        strict = flex = perm = fmt = 0
        correct = []
        for r in recs:
            t = r["output"]
            p = gsm_extract(t)
            fmt += p is not None
            s_ok = (p is not None and p.rstrip(".") == r["gold"])
            f = flex_num(t)
            f_ok = (f is not None and f == r["gold"])
            strict += s_ok; flex += f_ok
            # permissive = "the gold number appears where an answer would be",
            # i.e. either scoring rule accepts it.  Neither rule is a superset of
            # the other: `#### N` can be followed by more text, which defeats the
            # last-number rule.
            perm += (s_ok or f_ok)
            correct.append(int(s_ok or f_ok))   # permissive: the primary GSM8K vector
        out["acc"] = strict / n              # strict-match, as in the parent
        out["acc_flexible"] = flex / n
        out["acc_permissive"] = perm / n
        out["format_rate"] = fmt / n
        out["mean_out_chars"] = sum(len(r["output"]) for r in recs) / n

    elif cell == "squad_gen":
        has = hasx = noans = noans_ok = 0
        exact = 0
        correct = []          # HasAns_exact indicator, answerable items only
        for r in recs:
            pred = squad_norm(r["output"].strip().split("\n")[0])
            is_noans_pred = pred in ("", "unanswerable", "no answer", "none")
            if r["meta"]["answerable"]:
                has += 1
                ok = (not is_noans_pred) and any(
                    squad_norm(g) == pred for g in r["gold"])
                hasx += ok; exact += ok; correct.append(int(ok))
            else:
                noans += 1
                noans_ok += is_noans_pred; exact += is_noans_pred
        out["exact"] = 100 * exact / n
        out["HasAns_exact"] = 100 * hasx / has if has else None
        out["NoAns_acc"] = 100 * noans_ok / noans if noans else None
        # lm-eval `best_exact` can never go below the all-unanswerable baseline
        out["best_exact_floor"] = 100 * noans / n
        out["best_exact"] = max(out["exact"], out["best_exact_floor"])
        out["acc"] = out["best_exact"]
        out["mean_out_chars"] = sum(len(r["output"]) for r in recs) / n
    out["n_scored"] = n
    out["correct"] = correct
    out["item_ids"] = [r["id"] for r in recs]
    return out


def main():
    rows = []
    for p in sorted((ROOT / "results" / "e01").rglob("*.jsonl")):
        try:
            rows.append(score(p))
        except Exception as e:
            print("ERR", p, type(e).__name__, e, file=sys.stderr)
    (ROOT / "results" / "e01_summary.json").write_text(json.dumps(rows, indent=1))

    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["model"], r["cell"])][r["mask"]] = r
    print(f"{'model':<34}{'cell':<19}{'mask':<7}{'acc':>8}{'rel':>8}   extra")
    for (m, c), d in sorted(by.items()):
        base = d.get("full", {}).get("acc")
        for mask in ("full", "first", "last"):
            r = d.get(mask)
            if not r: continue
            rel = r["acc"] / base if base else float("nan")
            extra = " ".join(
                f"{k}={r[k]:.3f}" for k in
                ("acc_permissive", "acc_flexible", "format_rate", "HasAns_exact", "NoAns_acc", "best_exact_floor", "parse_rate", "mean_out_chars")
                if r.get(k) is not None)
            print(f"{m.split('/')[-1]:<34}{c:<19}{mask:<7}{r['acc']:>8.4f}{rel:>8.3f}   {extra}")
        print()


if __name__ == "__main__":
    main()
