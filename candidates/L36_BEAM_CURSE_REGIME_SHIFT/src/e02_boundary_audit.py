"""L36 — boundary-specificity audit.

The open reviewer attack on E02 is that unseen-format BLEU of 6-8 with ~4x length could mean the
wrapper breaks *more* than termination. This separates the two, with the interpretation rule fixed
in advance by `ACTIVE_PROJECT.md` / `search_rounds/2026-09-14_L36_PROMOTION_TO_MAIN_CANDIDATE.md`:

  content intact + stopping broken  ->  boundary-only causality stands and is strengthened
  content also broken               ->  retreat to "format-conditional generation contract",
                                        assert no boundary-only causality

Three diagnostics, both formats, every condition:

  D1  target-token NLL and top-1 accuracy over the reference translation, EXCLUDING <END>
  D2  first-span quality: BLEU of the full run-on output, of its first line, and of the output
      truncated to the reference's word count
  D3  end-hazard profile: p(<END> | reference prefix) across normalised position, and at the
      true end
"""

import argparse
import json
import os
import sys

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import mt_metrics as M                      # noqa: E402
from e02_train import FORMATS, END_TOKEN    # noqa: E402

NBINS = 10


@torch.no_grad()
def diagnostics(model, tok, srcs, refs_single, refs_multi, end_id, n_gen, batch=8):
    out = {}
    for fmt, template in FORMATS.items():
        nlls, accs, hz_bins, hz_end, hz_max_before = [], [], [], [], []
        # ---- D1 + D3: one teacher-forced pass over the reference ---------------------------
        for i in range(0, len(srcs), batch):
            cs, ct = srcs[i:i + batch], refs_single[i:i + batch]
            texts = [template.format(src=s) + t for s, t in zip(cs, ct)]
            enc = tok(texts, return_tensors="pt", padding=True,
                      add_special_tokens=False).to(model.device)
            logits = model(**enc).logits.float()
            lp = torch.log_softmax(logits, dim=-1)
            pred = logits.argmax(-1)
            for k, (s, t) in enumerate(zip(cs, ct)):
                n_pad = int((enc["attention_mask"][k] == 0).sum())
                n_prompt = len(tok(template.format(src=s), add_special_tokens=False)["input_ids"])
                start = n_pad + n_prompt - 1          # predicts the first target token
                end = enc["input_ids"].shape[1] - 1   # predicts the token after the last one
                if end <= start:
                    continue
                tgt = enc["input_ids"][k, start + 1:end + 1]
                tok_lp = lp[k, start:end].gather(1, tgt.unsqueeze(1)).squeeze(1)
                nlls.append(float(-tok_lp.mean()))
                accs.append(float((pred[k, start:end] == tgt).float().mean()))
                haz = lp[k, start:end + 1, end_id].exp()        # p(<END>) at each prefix
                hz_end.append(float(haz[-1]))
                if len(haz) > 1:
                    hz_max_before.append(float(haz[:-1].max()))
                    idx = np.linspace(0, len(haz) - 2, NBINS).astype(int)
                    hz_bins.append(haz[:-1][idx].tolist())
        # ---- D2: greedy generation, then three readings of the same output ------------------
        hyp_full, hyp_line, hyp_trunc = [], [], []
        for i in range(0, min(n_gen, len(srcs)), batch):
            cs = srcs[i:i + batch]
            enc = tok([template.format(src=s) for s in cs], return_tensors="pt", padding=True,
                      add_special_tokens=False).to(model.device)
            gen = model.generate(**enc, num_beams=1, do_sample=False, max_new_tokens=128,
                                 pad_token_id=tok.pad_token_id, eos_token_id=[end_id])
            gen = gen[:, enc["input_ids"].shape[1]:]
            for k in range(len(cs)):
                txt = tok.decode(gen[k], skip_special_tokens=True).strip()
                hyp_full.append(txt)
                hyp_line.append(txt.split("\n")[0].strip())
                n_ref = len(refs_single[i + k].split())
                hyp_trunc.append(" ".join(txt.split()[:n_ref]))
        rm = refs_multi[:len(hyp_full)]
        out[fmt] = {
            "n_scored": len(nlls),
            "target_nll": float(np.mean(nlls)),
            "target_top1_acc": float(np.mean(accs)),
            "p_end_at_true_end": float(np.mean(hz_end)),
            "p_end_max_before_end": float(np.mean(hz_max_before)) if hz_max_before else float("nan"),
            "hazard_profile": np.mean(np.array(hz_bins), axis=0).tolist() if hz_bins else [],
            "bleu_full": M.corpus_bleu(hyp_full, rm),
            "bleu_first_line": M.corpus_bleu(hyp_line, rm),
            "bleu_trunc_to_ref_len": M.corpus_bleu(hyp_trunc, rm),
            "len_ratio_full": float(np.mean([len(h.split()) for h in hyp_full]) /
                                    np.mean([len(r.split()) for r in refs_single[:len(hyp_full)]])),
            "sample_full": hyp_full[:2],
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--n-gen", type=int, default=100)
    a = ap.parse_args()

    data = os.path.join(ROOT, "data")
    src = [l.rstrip("\n") for l in open(f"{data}/newstest2019.en", encoding="utf-8")][:a.n]
    ref_w = [l.rstrip("\n") for l in open(f"{data}/newstest2019.wmtref.de", encoding="utf-8")][:a.n]
    ref_a = [l.rstrip("\n") for l in open(f"{data}/newstest2019.arref.de", encoding="utf-8")][:a.n]
    refs_multi = [[w, x] for w, x in zip(ref_w, ref_a)]

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    end_id = tok.convert_tokens_to_ids(END_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16,
                                                 device_map="cuda").eval()

    res = {"tag": a.tag, "model": a.model, "n": a.n, "n_gen": a.n_gen, "end_id": end_id,
           "formats": diagnostics(model, tok, src, ref_w, refs_multi, end_id, a.n_gen)}
    outp = os.path.join(ROOT, "results", "e02", f"audit_{a.tag}.json")
    with open(outp, "w") as f:
        json.dump(res, f, indent=2)
    for fmt, d in res["formats"].items():
        print(f"[{a.tag}/{fmt}] NLL {d['target_nll']:.3f}  acc {d['target_top1_acc']:.3f}  "
              f"BLEU full {d['bleu_full']:5.2f} / line {d['bleu_first_line']:5.2f} / "
              f"trunc {d['bleu_trunc_to_ref_len']:5.2f}  lenR {d['len_ratio_full']:.2f}  "
              f"p(END@end) {d['p_end_at_true_end']:.3f}  max before {d['p_end_max_before_end']:.4f}",
              flush=True)
    print("wrote", outp)


if __name__ == "__main__":
    main()
