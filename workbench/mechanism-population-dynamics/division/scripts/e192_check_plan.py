#!/usr/bin/env python3
"""E192 round 3: CPU bookkeeping check of the per-layer router treatment in e192_train.py (tiny model, 2 AdamW steps).
For every mode: which parameters train, which router layers are frozen (bit-unchanged after 2 steps, absent from the
optimizer and from the clip norm), which are reset (re-drawn exactly as the original all-layer reset: one generator, MoE
layers in order; zero Adam state, step 0 -> 2), all other tensors keep the loaded Adam state (step 1080 -> 1082).
usage: E192_COMPILE=0 CUDA_VISIBLE_DEVICES= python e192_check_plan.py"""
import os, sys
os.environ.setdefault("E192_COMPILE", "0")
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e192_train import Flame, router_plan, apply_router_plan, init_opt_state, BF  # noqa: E402

c = {"V": 100, "d": 32, "L": 4, "nh": 4, "ffn": 64, "E": 8, "K": 2, "fe": 16, "fs": 32, "eps": 1e-6, "theta": 1e4, "dense_layers": [0]}
STD, SEED = 0.02, 201
MODES = {"free": ("free", [], []), "frozen": ("frozen", [], []), "reset(all)": ("reset", [], []), "only": ("only", [], []),
         "CL1 (reset 1)": ("free", [], [1]), "CD (reset 2-3)": ("free", [], [2, 3]), "DL1free (freeze 2-3)": ("free", [2, 3], []),
         "DL1only (freeze 1)": ("free", [1], [])}
ok = True
for name, (router, fl, rl) in MODES.items():
    torch.manual_seed(0)
    m = Flame(c)
    for p in m.parameters():
        torch.nn.init.normal_(p, 0, 0.05)
    init = {n: p.detach().clone() for n, p in m.named_parameters()}
    moe = m.moe_layers()
    frozen, reset = router_plan(router, moe, fl, rl)
    reset_names = apply_router_plan(m, router, frozen, reset, SEED, STD, "cpu")
    # the original all-layer reset, for comparison
    if router == "reset":
        g = torch.Generator(device="cpu").manual_seed(SEED)
        for l in moe:
            exp = torch.randn(m.decoder.layers[l].mlp.router.weight.shape, generator=g) * STD
            ok &= torch.equal(exp, m.decoder.layers[l].mlp.router.weight.detach())
    after_reset = {n: p.detach().clone() for n, p in m.named_parameters()}
    named = [(n, p) for n, p in m.named_parameters() if p.requires_grad]
    adam = {n: (torch.full_like(p, 1e-4), torch.full_like(p, 1e-6)) for n, p in m.named_parameters()}
    opt = torch.optim.AdamW([{"params": [p for n, p in named if p.ndim > 1], "weight_decay": .01},
                             {"params": [p for n, p in named if p.ndim <= 1], "weight_decay": 0.0}], lr=3e-4, betas=(.9, .999), eps=1e-8)
    init_opt_state(opt, named, adam, 1080.0, reset_names, "cpu")
    ids = torch.randint(0, 100, (2, 17))
    for _ in range(2):
        x = m(ids[:, :-1], {"aux_on": False}); loss = m.lm_loss(x, ids[:, 1:])
        loss.backward()
        torch.nn.utils.clip_grad_norm_([p for _, p in named], 1.0)
        opt.step(); opt.zero_grad(set_to_none=True)
    rows = []
    for l in moe:
        n = f"decoder.layers.{l}.mlp.router.weight"; p = dict(m.named_parameters())[n]
        state = "frozen" if l in frozen else ("reset" if n in reset_names else "free")
        unchanged = torch.equal(p.detach(), after_reset[n]); redrawn = not torch.equal(after_reset[n], init[n])
        in_opt = any(q is p for _, q in named); step = float(opt.state[p]["step"]) if p in opt.state else None
        exp_ok = {"frozen": unchanged and not in_opt and not redrawn,
                  "reset": redrawn and in_opt and step == 2.0 and not unchanged,
                  "free": (not redrawn) and in_opt and step == 1082.0 and not unchanged}[state] if router != "only" else in_opt
        ok &= exp_ok
        rows.append(f"L{l}:{state}{'' if exp_ok else '!!'}(step {step}, unchanged {unchanged})")
    others = [n for n, p in m.named_parameters() if not n.endswith("router.weight")]
    if router == "only":
        oth_ok = all(torch.equal(dict(m.named_parameters())[n].detach(), init[n]) for n in others)
    else:
        oth_ok = all(float(opt.state[dict(m.named_parameters())[n]]["step"]) == 1082.0 for n in others)
    ok &= oth_ok
    print(f"{name:24s} frozen={sorted(frozen)} reset={reset} n_trainable={len(named)} | " + " ".join(rows) + f" | non-router ok {oth_ok}")
print("ALL CHECKS PASSED" if ok else "CHECK FAILED")
