"""CT03 E01 section 8 -- implementation validity checks.

Run and pass this BEFORE reading any headline number from e01_credit.py.
It checks three things that, if wrong, would silently manufacture a result:

  1. replay identity    -- replaying layers l+1.. from a captured layer output
                           reproduces the full forward's CE.
  2. route algebra      -- the MoE output recomputed from the router's own
                           top-k weights matches the block's output, and the
                           swapped route's output matches h + dh.
  3. exact = exact      -- the replay-based dL_seq equals the dL_seq from a
                           genuine full forward with a routing-override hook.
"""

import json, sys, torch, torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from e01_credit import MODEL, Capture, replay_ce

dev = "cuda"
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32,
                                             attn_implementation="sdpa").to(dev).eval()
for p in model.parameters():
    p.requires_grad_(False)
K = model.config.num_experts_per_tok
LAYERS = [1, 7, 15]

ex = load_dataset("HuggingFaceH4/MATH-500", split="test")[3]
prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                 tokenize=False, add_generation_prompt=True)
p_ids = tok(prompt, add_special_tokens=False).input_ids
s_ids = tok(ex["solution"], add_special_tokens=False).input_ids[:200]
ids = p_ids + s_ids
input_ids = torch.tensor([ids], device=dev)
targets = input_ids[0, 1:]
first = len(p_ids) - 1
t = first + len(s_ids) // 2

with Capture(model, LAYERS) as cap:
    with torch.no_grad():
        logits = model(input_ids).logits
        base_ce = F.cross_entropy(logits[0, :-1].float(), targets, reduction="none")
    mlp_in = {l: cap.mlp_in[l].detach() for l in LAYERS}
    mlp_out = {l: cap.mlp_out[l].detach() for l in LAYERS}
    layer_out = {l: cap.layer_out[l].detach() for l in LAYERS}
    attn_kwargs = cap.attn_kwargs

report = {}
ok = True

# --- 1. replay identity -------------------------------------------------
for l in LAYERS:
    rep = replay_ce(model, l, layer_out[l].clone(), t, targets, attn_kwargs)[0]
    d = (rep - base_ce[t:]).abs().max().item()
    report[f"replay_identity_L{l}_max_abs_ce_diff"] = d
    ok &= d < 1e-3

# --- 2. route algebra ---------------------------------------------------
for l in LAYERS:
    moe = model.model.layers[l].mlp
    x = mlp_in[l][0, t]
    w = F.softmax(moe.gate(x).float(), dim=-1)
    rank = torch.argsort(w, descending=True)
    sel = rank[:K].tolist()
    h_rebuilt = sum(moe.experts[e](x) * w[e] for e in sel)
    d1 = (h_rebuilt - mlp_out[l][0, t]).abs().max().item()
    i_rep, j = sel[-1], int(rank[K])
    h_swap = sum(moe.experts[e](x) * w[e] for e in sel[:-1]) + moe.experts[j](x) * w[j]
    dh = moe.experts[j](x) * w[j] - moe.experts[i_rep](x) * w[i_rep]
    d2 = (h_swap - (mlp_out[l][0, t] + dh)).abs().max().item()
    report[f"route_algebra_L{l}_rebuild_err"] = d1
    report[f"route_algebra_L{l}_swap_err"] = d2
    ok &= d1 < 1e-3 and d2 < 1e-3

# --- 3. replay dL_seq == full-forward dL_seq ----------------------------
base_sum = base_ce[first:].sum().item()
for l in LAYERS:
    moe = model.model.layers[l].mlp
    x = mlp_in[l][0, t]
    w = F.softmax(moe.gate(x).float(), dim=-1)
    rank = torch.argsort(w, descending=True)
    sel = rank[:K].tolist()
    i_rep, j = sel[-1], int(rank[K])
    dh = (moe.experts[j](x) * w[j] - moe.experts[i_rep](x) * w[i_rep]).detach()

    H = layer_out[l].clone()
    H[:, t] += dh
    rep = replay_ce(model, l, H, t, targets, attn_kwargs)[0]
    dL_replay = (rep - base_ce[t:]).sum().item()

    hd = model.model.layers[l].mlp.register_forward_hook(
        lambda m, i_, o, dh=dh, t=t: (o[0].index_copy(
            1, torch.tensor([t], device=dev), (o[0][:, t] + dh).unsqueeze(1)), o[1]))
    with torch.no_grad():
        lg = model(input_ids).logits
        ce2 = F.cross_entropy(lg[0, :-1].float(), targets, reduction="none")
    hd.remove()
    dL_full = ce2[first:].sum().item() - base_sum

    report[f"exact_L{l}_dL_replay"] = dL_replay
    report[f"exact_L{l}_dL_full_forward"] = dL_full
    report[f"exact_L{l}_abs_diff"] = abs(dL_replay - dL_full)
    ok &= abs(dL_replay - dL_full) < max(1e-3, 0.02 * abs(dL_full))

report["ALL_PASS"] = bool(ok)
print(json.dumps(report, indent=1))
sys.exit(0 if ok else 1)
