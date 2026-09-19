"""CT03 E01 section 7 -- analytic cost of exact vs proxy counterfactual credit.

The measured wall-clock in e01_records.jsonl is for the *batched* exact replay,
so it already amortises over the candidate pool. This adds the analytic FLOPs
side, which is what transfers to other models.
"""
import json, numpy as np

D, F, E, K, L, V = 2048, 1024, 64, 8, 16, 50304  # OLMoE-1B-7B

def expert_flops():           # one expert MLP, one token (gate+up+down)
    return 2 * 3 * D * F

def attn_flops(T):            # qkv+o projections, one token, ignoring the T*D score term
    return 2 * 4 * D * D + 2 * 2 * T * D

def layer_flops(T):           # one decoder layer, one token
    return attn_flops(T) + K * expert_flops()

recs = [json.loads(l) for l in open("results/e01_records.jsonl")]
T = float(np.mean([r["seq_len"] for r in recs]))
first = float(np.mean([r["first"] for r in recs]))
pos = float(np.mean([r["pos"] for r in recs]))
tail = T - pos                # positions replayed (only t.. matter)

# The shared backward is paid ONCE per sequence and amortised over every
# candidate harvested from it. It dominates the local expert forward, so the
# honest per-candidate proxy cost must include it -- quoting only the expert
# MLP would inflate the advantage by three orders of magnitude.
bwd = 2 * L * T * layer_flops(T) + 2 * T * 2 * D * V
cands = 6 * 8 * 16            # layers x tokens x candidates, as run
bwd_per_cand = bwd / cands

out = {"mean_seq_len": T, "mean_pos": pos, "mean_replayed_positions": tail,
       "candidates_per_sequence": cands, "by_layer": {}}
for l in (1, 4, 7, 10, 13, 15):
    exact = (L - 1 - l) * tail * layer_flops(T) + tail * 2 * D * V
    proxy_local = expert_flops()          # ONE unexecuted expert, ONE token
    proxy_total = proxy_local + bwd_per_cand
    meas = float(np.mean([r["exact_batch_s"] / r["n_cand"] for r in recs if r["layer"] == l]))
    out["by_layer"][l] = dict(
        exact_gflops=exact / 1e9, proxy_local_mflops=proxy_local / 1e6,
        proxy_total_gflops=proxy_total / 1e9,
        ratio_local_only=exact / proxy_local,
        ratio_honest=exact / proxy_total,
        measured_exact_s_per_cand=meas)

out["shared_backward_gflops"] = bwd / 1e9
out["shared_backward_gflops_per_candidate"] = bwd_per_cand / 1e9
json.dump(out, open("results/e01_cost.json", "w"), indent=1)

print(f"mean seq len {T:.0f}, mean swap position {pos:.0f}, replayed tail {tail:.0f}\n")
print(f"{'layer':>6}{'exact GFLOP':>13}{'proxy GFLOP':>13}{'honest x':>10}"
      f"{'local-only x':>14}{'measured s':>12}")
for l, v in out["by_layer"].items():
    print(f"{l:>6}{v['exact_gflops']:>13.1f}{v['proxy_total_gflops']:>13.2f}"
          f"{v['ratio_honest']:>10,.0f}{v['ratio_local_only']:>14,.0f}"
          f"{v['measured_exact_s_per_cand']:>12.4f}")
print(f"\nshared backward: {out['shared_backward_gflops']:.1f} GFLOP once per sequence "
      f"= {out['shared_backward_gflops_per_candidate']:.3f} GFLOP per candidate at the "
      f"{cands} candidates/sequence this run used")
