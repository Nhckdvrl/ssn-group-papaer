"""Summarise E04 generation runs (node-local jsonl) into one JSON with accuracy, format and style readouts.
Usage: python3 e04_gen_summary.py <out_json> <tag> [<tag> ...]   (reads /tmp/xiang_lmhead/e04/gen/<tag>.jsonl)"""
import json
import random
import re
import sys
from pathlib import Path

GEN = Path("/tmp/xiang_lmhead/e04/gen")
MARKERS = {"bold": r"\*\*", "heading": r"^#{2,}", "check_emoji": "✅", "final_answer": r"Final Answer", "boxed": r"\\boxed",
           "wait": r"\bWait\b", "hr": r"^---", "answer_line": r"^Answer:", "think_tag": r"</?think>"}


def degenerate(text, n=12):
    tail = text[-400:]
    if len(tail) < 200:
        return False
    for k in range(2, n + 1):
        unit = tail[-k:]
        if unit.strip() and tail.endswith(unit * max(4, 60 // k)):
            return True
    return False


def summarise(tag):
    rows = [json.loads(l) for l in open(GEN / f"{tag}.jsonl")]
    meta = json.loads((GEN / f"{tag}.meta.json").read_text())
    per_q = [sum(c["reward"] for c in r["completions"]) / len(r["completions"]) for r in rows]
    comps = [c for r in rows for c in r["completions"]]
    rng = random.Random(0)
    boots = sorted(sum(per_q[rng.randrange(len(per_q))] for _ in per_q) / len(per_q) for _ in range(2000))
    out = {"tag": tag, "model": meta["model"], "tau": meta["tau"], "bias_key": meta.get("bias_key") if meta.get("bias") else None,
           "bias_scale": meta.get("bias_scale"), "n_q": len(rows), "acc": sum(per_q) / len(per_q), "acc_ci95": [boots[50], boots[1949]],
           "parse_fail": sum(c["pred"] is None for c in comps) / len(comps),
           "truncated": sum(c["finish"] == "length" for c in comps) / len(comps),
           "degenerate": sum(degenerate(c["text"]) for c in comps) / len(comps),
           "mean_len": sum(len(c["token_ids"]) for c in comps) / len(comps)}
    for k, pat in MARKERS.items():
        out[f"rate_{k}"] = sum(bool(re.search(pat, c["text"], re.M)) for c in comps) / len(comps)
    return out


if __name__ == "__main__":
    res = [summarise(t) for t in sys.argv[2:] if (GEN / f"{t}.jsonl").exists()]
    Path(sys.argv[1]).write_text(json.dumps(res, indent=1))
    for r in res:
        print(f"{r['tag']:18s} acc {r['acc']:.3f} [{r['acc_ci95'][0]:.3f},{r['acc_ci95'][1]:.3f}] parse {r['parse_fail']:.3f} "
              f"trunc {r['truncated']:.3f} degen {r['degenerate']:.3f} len {r['mean_len']:.0f} | bold {r['rate_bold']:.2f} "
              f"head {r['rate_heading']:.2f} ✅ {r['rate_check_emoji']:.2f} FA {r['rate_final_answer']:.2f} boxed {r['rate_boxed']:.2f} "
              f"wait {r['rate_wait']:.2f} ans {r['rate_answer_line']:.2f}")
