"""Plumbing: (1) no-drop, self-sourced rows == one plain forward over ctx+query+probe+value;
(2) p_drop rows differ; (3) FULL_NAT free-running answer sanity on a few items."""
import json, sys, torch
from handoff import load, prefill, run_rows
tok, model = load(sys.argv[1])
T = lambda x: torch.tensor(x, device="cuda")
for it in [json.loads(l) for l in open(sys.argv[2])][:4]:
    N, q, p, va = it["N"], it["q_late"], it["p_late"], it["val_ids"]["A"]
    full = T(it["ctx"]["A"] + q + p + va)
    with torch.no_grad():
        lp = torch.log_softmax(model(input_ids=full[None]).logits.float(), -1)[0]
    n = len(va); ref = sum(lp[len(full) - n - 1 + i, va[i]].item() for i in range(n))
    c = {k: prefill(model, T(it["ctx"][k])) for k in ("A", "0")}
    out = run_rows(model, N, [c["A"]] * 3, [c["A"], c["A"], c["0"]], T(q), [False] * 3,
                   T([p + va] * 3), [False, True, False], n)
    g = model.generate(T(it["ctx"]["A"] + q)[None], max_new_tokens=8, do_sample=False)
    print(it["id"], "N", N, "ref", round(ref, 3), "cached", [round(x, 3) for x in out.tolist()],
          "| vA", it["vA"], "gen:", repr(tok.decode(g[0, N + len(q):])))
