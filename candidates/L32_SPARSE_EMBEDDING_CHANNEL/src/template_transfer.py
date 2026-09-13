"""Validity check on the channel result: is the ticket a task locus or a template key?

E01's channel arms show the learned update acts entirely through its occurrences
in the fixed instruction span. Two readings survive that:

  (i)  the rows encode a translation/task capability that happens to be injected
       at the instruction positions -- the parent's reading;
  (ii) the rows encode a prompt keyed to the *particular* template the delta was
       trained under.

These differ in exactly one observable: swap the template at inference, change
nothing else. (i) predicts the gain largely survives. (ii) predicts it collapses.

Added to E01 as an instrument check (notes/E01_DESIGN.md §7) and disclosed as
such -- it introduces no new trained model and no new estimand.
"""
import argparse
import json
import pathlib
import sys

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/xiang/.cache/l32/pylibs")
from common import (ROOT, SEG_INSTR, SEG_INSTR_TAIL, SEG_SOURCE,  # noqa: E402
                    SparseDelta, load_backbone, read_jsonl)
from eval import generate, load_delta  # noqa: E402

# (head, tail). "explicit" is the template the delta was trained under.
TEMPLATES = {
    "explicit": ("Translate the following sentence from English to Catalan.\nEnglish:",
                 "\nCatalan:"),
    "paraphrase": ("Please render the next English sentence into Catalan.\nSource:",
                   "\nTarget:"),
    "bare_pair": ("English:", "\nCatalan:"),
    "reordered": ("\nCatalan translation of the English below.\nEnglish:", "\nCatalan:"),
}


def build(tok, src, head, tail):
    a = tok.encode(head, add_special_tokens=False)
    ab = tok.encode(head + " " + src, add_special_tokens=False)
    abc = tok.encode(head + " " + src + tail, add_special_tokens=False)
    if ab[: len(a)] != a or abc[: len(ab)] != ab:
        return None, None
    seg = ([SEG_INSTR] * len(a) + [SEG_SOURCE] * (len(ab) - len(a))
           + [SEG_INSTR_TAIL] * (len(abc) - len(ab)))
    return [tok.bos_token_id] + abc, [SEG_INSTR] + seg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--delta", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--limit", type=int, default=400)
    ap.add_argument("--batch-size", type=int, default=24)
    ap.add_argument("--max-new", type=int, default=256)
    args = ap.parse_args()

    base_rows = read_jsonl(ROOT / "data" / "devtest_en_ca.jsonl")[: args.limit]
    model, tok = load_backbone(args.model)
    model.eval()
    emb = model.get_input_embeddings()
    tuned = load_delta(model, args.delta)
    zero = SparseDelta(model.config.hidden_size).cuda()
    from sacrebleu.metrics import BLEU
    bleu = BLEU(tokenize="flores101")
    refs = [r["ref"] for r in base_rows]

    out = {}
    for name, (head, tail) in TEMPLATES.items():
        rows = []
        for r in base_rows:
            ids, seg = build(tok, r["src"], head, tail)
            if ids is None:
                continue
            rows.append({"ids": ids, "seg": seg, "y": r["y"], "ref": r["ref"]})
        rr = [r["ref"] for r in rows]
        out[name] = {"n": len(rows)}
        for cond, d in (("BASE", zero), ("ALL", tuned)):
            gen, stopped = generate(model, emb, d, rows, "ALL" if cond == "ALL" else "BASE",
                                    tok.eos_token_id, tok.eos_token_id,
                                    args.max_new, args.batch_size)
            raw = [" ".join(tok.decode(g, skip_special_tokens=True).split()) for g in gen]
            trunc = [tok.decode(g, skip_special_tokens=True).strip().split("\n")[0].strip()
                     for g in gen]
            out[name][cond] = {
                "raw": bleu.corpus_score(raw, [rr]).score,
                "trunc": bleu.corpus_score(trunc, [rr]).score,
                "stop": sum(stopped) / len(stopped),
                "chars": sum(len(x) for x in raw) / len(raw),
            }
        b, a = out[name]["BASE"], out[name]["ALL"]
        out[name]["delta_raw"] = a["raw"] - b["raw"]
        print(f"{name:<12} BASE raw {b['raw']:6.2f} trunc {b['trunc']:6.2f} stop {b['stop']:.2f}"
              f" | ALL raw {a['raw']:6.2f} trunc {a['trunc']:6.2f} stop {a['stop']:.2f}"
              f" | delta_raw {out[name]['delta_raw']:+6.2f}", flush=True)

    p = ROOT / "results" / f"template_transfer_{args.tag}.json"
    p.write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
