"""CT03 Stage B condition 6 -- cost of exact vs proxy on Qwen3-30B-A3B."""
import json
import numpy as np
from transformers import AutoConfig

c = AutoConfig.from_pretrained("Qwen/Qwen3-30B-A3B")
D, F_, E, K, L, V = (c.hidden_size, c.moe_intermediate_size, c.num_experts,
                     c.num_experts_per_tok, c.num_hidden_layers, c.vocab_size)
HD = getattr(c, "head_dim", D // c.num_attention_heads)
QH, KVH = c.num_attention_heads, c.num_key_value_heads

expert = 2 * 3 * D * F_


def attn(T):
    proj = 2 * D * (QH * HD) + 2 * 2 * D * (KVH * HD) + 2 * (QH * HD) * D
    return proj + 2 * 2 * T * QH * HD


def layer(T):
    return attn(T) + K * expert


recs = [json.loads(l) for l in open("results/e02_records.jsonl")]
T = float(np.mean([r["seq_len"] for r in recs]))
tail = float(np.mean([r["seq_len"] - r["pos"] for r in recs]))
bwd = 2 * L * T * layer(T) + 2 * T * 2 * D * V

out = dict(model="Qwen/Qwen3-30B-A3B", n_layers=L, n_experts=E, top_k=K,
           hidden=D, moe_inter=F_, vocab=V, mean_seq_len=T, mean_tail=tail,
           expert_mflops=expert / 1e6, shared_backward_gflops=bwd / 1e9)

print(f"Qwen3-30B-A3B  L={L} E={E} K={K} D={D} F={F_} V={V}")
print(f"mean seq len {T:.0f}, mean replayed tail {tail:.0f}")
print(f"one expert forward: {expert/1e6:.2f} MFLOP   shared backward: {bwd/1e9:.0f} GFLOP\n")

print("cost ratio (exact / proxy) vs candidates harvested per shared backward")
LY = [20, 28, 36, 44, 47]
print(f"{'cands/seq':>10}" + "".join(f"{'L'+str(l):>9}" for l in LY))
tab = {}
for n in (4, 8, 16, 32, 64, 256, 840, 4096, 16384):
    proxy = 2 * expert + bwd / n          # candidate expert + replaced expert
    row = []
    for l in LY:
        exact = (L - 1 - l) * tail * layer(T) + tail * 2 * D * V
        row.append(exact / proxy)
    tab[n] = row
    print(f"{n:>10}" + "".join(f"{v:>9.1f}" for v in row))
out["ratio_by_cands"] = {str(k): v for k, v in tab.items()}

print("\nbreak-even candidates/sequence (ratio = 1x):")
be = {}
for l in LY:
    exact = (L - 1 - l) * tail * layer(T) + tail * 2 * D * V
    be[l] = bwd / (exact - 2 * expert) if exact > 2 * expert else float("inf")
    print(f"  L{l:<3} ({l/L:.0%} depth): {be[l]:8.1f}")
out["break_even"] = be

meas = {}
for l in sorted({r["layer"] for r in recs}):
    v = [r["batch_s"] / (r["n_rows"] - 2) for r in recs if r["layer"] == l]
    meas[l] = float(np.mean(v))
out["measured_exact_s_per_candidate"] = meas
print("\nmeasured exact seconds per candidate (batched, fp32, 2 cards):")
for l, v in meas.items():
    print(f"  L{l:<3}: {v:.4f}")
json.dump(out, open("results/e02_cost.json", "w"), indent=1)
print("\nwrote results/e02_cost.json")
