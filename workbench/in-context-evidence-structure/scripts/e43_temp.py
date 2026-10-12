"""E43 a: soften (temperature T) the answer-position attention of the E36 label-reading heads and measure order
sensitivity vs evidence.  usage: e43_temp.py --model Qwen/Qwen3-8B --tag Qwen3-8B --out NPZ
Temperature is applied by scaling the post-q_norm query vector of the chosen heads at the last position by 1/T
(RoPE is a rotation, so attention logits scale by 1/T).  Conditions: T in {1, 1.5, 2, 3} on top-20 heads, and
T in {2, 3} on 20 layer-matched random heads.  Data: kernel_perm (240 bases x 8 orders)."""
import argparse, json, random, sys
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--tag"); ap.add_argument("--out"); ap.add_argument("--bs", type=int, default=24)
    a = ap.parse_args()
    from mech_ablate import rows_by_task, select_heads
    R, _ = rows_by_task()
    sets = select_heads(a.tag, R)["mag_nat"]
    top, rand = sets["top20"], sets["rand"][0]
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="sdpa").eval()
    state = {"scale": {}}

    def hook(l):
        def f(mod, args, out):
            if l in state["scale"]:
                out = out.clone()
                for h, s in state["scale"][l]:
                    out[:, -1, h, :] *= s
                return out
        return f
    for l, layer in enumerate(model.model.layers):
        layer.self_attn.q_norm.register_forward_hook(hook(l))
    rows = [json.loads(l) for l in open(ROOT / "data/kernel_perm/rows.jsonl")]
    enc = [tok(r["prompt"], add_special_tokens=False)["input_ids"] for r in rows]
    cid = [(tok(r["cands"][0], add_special_tokens=False)["input_ids"][0], tok(r["cands"][1], add_special_tokens=False)["input_ids"][0]) for r in rows]
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0

    def run():
        out = np.zeros(len(rows), np.float32)
        order = sorted(range(len(rows)), key=lambda i: -len(enc[i]))
        for s in range(0, len(order), a.bs):
            ix = order[s:s + a.bs]; Lm = max(len(enc[i]) for i in ix)
            ids = torch.full((len(ix), Lm), pad, dtype=torch.long); att = torch.zeros((len(ix), Lm), dtype=torch.long)
            for j, i in enumerate(ix):
                ids[j, Lm - len(enc[i]):] = torch.tensor(enc[i]); att[j, Lm - len(enc[i]):] = 1
            pos = (att.cumsum(1) - 1).clamp(min=0)
            lo = model(input_ids=ids.cuda(), attention_mask=att.cuda(), position_ids=pos.cuda(), logits_to_keep=1, use_cache=False).logits[:, -1].float()
            for j, i in enumerate(ix):
                out[i] = float(lo[j, cid[i][1]] - lo[j, cid[i][0]])
        return out
    conds = {"T1": (top, 1.0), "top_T1.5": (top, 1.5), "top_T2": (top, 2.0), "top_T3": (top, 3.0),
             "rand_T2": (rand, 2.0), "rand_T3": (rand, 3.0)}
    res = {}
    for name, (heads, T) in conds.items():
        state["scale"] = {}
        for l, h in heads:
            state["scale"].setdefault(l, []).append((h, 1.0 / T))
        res[name] = run(); print(name, "done", flush=True)
    np.savez_compressed(a.out, uid=np.array([r["uid"] for r in rows]), **res)


if __name__ == "__main__":
    main()
