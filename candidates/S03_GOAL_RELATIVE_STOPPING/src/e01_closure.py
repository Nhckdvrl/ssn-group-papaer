"""
S03 / E01 control — pretrained TEXTUAL-CLOSURE propensity per stimulus prefix.

The goal manipulation cannot be explained by textual closure *within* a pair
(the prefix is token-identical, so closure is constant by construction).  What
this control establishes is coverage and level attribution:

  * the exact-prefix goal effect must be present across prefixes that span a
    wide range of pretrained closure, not only where the base model already
    thinks the text is over;
  * it gives a continuous covariate so we can check whether d_goal is merely
    tracking how "finished" the prefix already looks to the pretrained model.

Measured on the BASE checkpoint, in a plain document context with no user goal
present at all:

    "<neutral list header>\n<prefix_text>"   ->  p(<|endoftext|>) at the end
"""
import argparse, json, os
import torch, torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
from e01_run import STAGE_REPOS


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", default="olmo2-1b")
    ap.add_argument("--stimuli", default="stimuli/e01_pairs.jsonl")
    args = ap.parse_args()
    repo = STAGE_REPOS[args.family]["base"]
    tok = AutoTokenizer.from_pretrained(repo)
    model = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.bfloat16,
                                                 device_map="cuda").eval()
    eos = tok.eos_token_id
    nl = tok.encode("\n", add_special_tokens=False)[0]
    items = [json.loads(l) for l in open(args.stimuli)]
    rows = []
    for it in items:
        # no goal, no instruction: just the raw material as a piece of document
        text = it["prefix_text"]
        ids = tok.encode(text, add_special_tokens=False)
        logits = model(torch.tensor([ids], device=model.device)).logits[0, -1].float()
        p = F.softmax(logits, dim=-1)
        # also after the separator, matching the p2 decision position
        ids2 = ids + tok.encode(it["separator"], add_special_tokens=False)
        logits2 = model(torch.tensor([ids2], device=model.device)).logits[0, -1].float()
        p2 = F.softmax(logits2, dim=-1)
        rows.append(dict(
            item_id=it["item_id"], family=it["family"],
            closure_logit_p1=float(logits[eos]), closure_p_p1=float(p[eos]),
            closure_margin_p1=float(logits[eos] - logits[nl]),
            closure_logit_p2=float(logits2[eos]), closure_p_p2=float(p2[eos]),
            closure_top5_p2=[tok.convert_ids_to_tokens(int(i))
                             for i in torch.topk(logits2, 5).indices],
        ))
    os.makedirs("results/e01", exist_ok=True)
    out = f"results/e01/closure_{args.family}.jsonl"
    with open(out, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", out, len(rows))


if __name__ == "__main__":
    main()
