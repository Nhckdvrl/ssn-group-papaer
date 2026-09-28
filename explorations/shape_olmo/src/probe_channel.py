"""Channel dissociation on the probe_order v2 items (Olmo-Hybrid only, transformers 5.12).

Conditions (one forward per item each):
  full    : normal model.
  reconly : at the query tokens, the full-attention layers cannot attend to the context region
            [SINK, query_start); GDN layers still process everything. The answer can only reach the
            readout through the recurrent (GDN + short-conv) state. Earlier positions attend
            normally.
Readout as in probe_order: log-probs of the n candidate values at the last position.

usage: probe_channel.py MODEL_PATH TAG   -> results/probe_channel/<TAG>.jsonl
"""
import json, os, sys
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_order import items

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SINK = 4
MASK = {"m": None}


def patch():
    import transformers.models.olmo_hybrid.modeling_olmo_hybrid as mh
    orig = mh.OlmoHybridAttention.forward

    def fwd(self, hidden_states, position_embeddings, attention_mask, past_key_values=None, **kw):
        if MASK["m"] is not None:
            attention_mask = MASK["m"]
        return orig(self, hidden_states, position_embeddings, attention_mask, past_key_values, **kw)
    mh.OlmoHybridAttention.forward = fwd


@torch.no_grad()
def main(path, tag):
    patch()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16, device_map="cuda",
                                                 attn_implementation="sdpa").eval()
    os.makedirs(f"{ROOT}/results/probe_channel", exist_ok=True)
    with open(f"{ROOT}/results/probe_channel/{tag}.jsonl", "w") as f:
        for it in items(tok):
            enc = tok(it["text"], add_special_tokens=False, return_offsets_mapping=True)
            ids = enc.input_ids
            qchar = it["text"].rfind("\nassert")
            qstart = next(i for i, (a, b) in enumerate(enc.offset_mapping) if b > qchar)
            L = len(ids)
            x = torch.tensor(ids, device="cuda")[None]
            out = {}
            for cond in ("full", "reconly"):
                if cond == "full":
                    MASK["m"] = None
                else:
                    m = torch.tril(torch.ones(L, L, dtype=torch.bool, device="cuda"))
                    m[qstart:, SINK:qstart] = False
                    MASK["m"] = m[None, None]
                lp = torch.log_softmax(model(input_ids=x).logits[0, -1].float(), -1)
                out[cond] = lp[it["cands"]].cpu().numpy().tolist()
            MASK["m"] = None
            f.write(json.dumps(dict(task=it["task"], n=it["n"], gap=it["gap"], k=it["k"], correct=it["correct"],
                                    lp_full=out["full"], lp_reconly=out["reconly"], len=L, qstart=qstart)) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
