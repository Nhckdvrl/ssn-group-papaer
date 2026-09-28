"""Is the cross-treatment control actually quality-matched?

The `foreign` arm assumes the two treated prefixes are of comparable quality, so that
Y(foreign) - Y(F) isolates WHICH perturbation produced the prefix rather than how good
it is.  That assumption has to be checked, not asserted -- it is the assumption whose
failure invalidated the corrupted-reference arm.

Over the clamped span only (k tokens, k from the reference trajectory), per prefix:
  on_task        fraction of the reference problem's numbers that appear
  has_calc       contains a well-formed <<a op b=c>> annotation
  calc_correct   ... and every such annotation is arithmetically right
  degenerate     repetition index: 8 x (count of the most frequent 8-token window)
                 divided by span length.  Overlapping windows make this exceed 1 for
                 heavily repetitive text, so it is a relative index, not a fraction.
"""
from __future__ import annotations
import importlib.util, json, pathlib, re, sys, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
ROOT = pathlib.Path(__file__).resolve().parents[1]
cs = importlib.util.spec_from_file_location("clamp", ROOT / "scripts" / "run_e12_clamp.py")
clamp = importlib.util.module_from_spec(cs); cs.loader.exec_module(clamp)
from transformers import AutoTokenizer

CALC = re.compile(r"<<\s*([-\d\.\+\*/\(\) ,]+?)\s*=\s*(-?[\d\.,]+)\s*>>")
NUM = re.compile(r"\d[\d,]*\.?\d*")


def calc_ok(text):
    hits = CALC.findall(text)
    if not hits:
        return None
    for expr, stated in hits:
        try:
            got = eval(expr.replace(",", ""), {"__builtins__": {}}, {})
            if abs(float(got) - float(stated.replace(",", ""))) > 1e-6:
                return False
        except Exception:
            return False
    return True


def degeneracy(toks):
    if len(toks) < 16:
        return 0.0
    w = collections.Counter(tuple(toks[i:i + 8]) for i in range(len(toks) - 7))
    return w.most_common(1)[0][1] * 8 / len(toks)


def main(tag="llama31_8b_instruct", cell="gsm8k_gen_cot", frac=0.5):
    tok = AutoTokenizer.from_pretrained("NousResearch/Meta-Llama-3.1-8B-Instruct")
    refs = clamp.reference_table(tok, ROOT / "results" / "e01" / tag / f"{cell}__full.jsonl", cell)
    items = {}
    for line in open(ROOT / "results" / "e01" / tag / f"{cell}__full.jsonl"):
        r = json.loads(line)
        if not r.get("_meta"):
            items[r["id"]] = r
    sources = {
        "reference Z(0)": ROOT / "results" / "e01" / tag / f"{cell}__full.jsonl",
        "readout Z(T)": ROOT / "results" / "e12" / tag / f"{cell}__readoutfirst__none__f0.jsonl",
        "prune Z(T')": ROOT / "results" / "e12" / tag / f"{cell}__prune0.4__none__f0.jsonl",
        "corrupted Z~(0)": ROOT / "results" / "e12" / tag / f"{cell}__corrupted_ref__readoutfirst__f0.5.jsonl",
        "surgical Z~s(0)": ROOT / "results" / "e12" / tag / f"{cell}__surgical_ref.jsonl",
    }
    print(f"prefix quality over the clamped span, frac={frac:g}\n")
    print(f"{'source':<18}{'on_task':>9}{'has_calc':>10}{'calc_ok|has':>12}{'degenerate':>12}{'n':>6}")
    for name, p in sources.items():
        if not p.exists():
            print(f"{name:<18}{'(missing)':>9}"); continue
        on, hc, ok, dg, n = 0.0, 0, 0, 0.0, 0
        for line in open(p):
            r = json.loads(line)
            if r.get("_meta") or r["id"] not in refs or refs[r["id"]]["L0"] is None:
                continue
            k = int(round(frac * refs[r["id"]]["L0"]))
            if k == 0:
                continue
            ids = tok(r.get("output", "") or "", add_special_tokens=False)["input_ids"][:k]
            span = tok.decode(ids, skip_special_tokens=True)
            gold_nums = set(NUM.findall(items[r["id"]]["meta"].get("gold_cot", "")))
            span_nums = set(NUM.findall(span))
            on += len(gold_nums & span_nums) / max(len(gold_nums), 1)
            c = calc_ok(span)
            if c is not None:
                hc += 1; ok += int(c)
            dg += degeneracy(ids); n += 1
        print(f"{name:<18}{on/n:>9.3f}{hc/n:>10.3f}"
              f"{(ok/hc if hc else float('nan')):>12.3f}{dg/n:>12.3f}{n:>6}")


if __name__ == "__main__":
    main()
