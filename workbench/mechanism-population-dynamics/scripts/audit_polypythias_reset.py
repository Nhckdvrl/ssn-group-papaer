"""Re-verification (2026-10-25) of PAIN_LOG P14 / E95: PolyPythias-410M seed3 / seed4 weights reset to their own step0.
Usage: audit_polypythias_reset.py DIR   (DIR holds pythia-410m-<seed>_step<N>.bin for seed3 0/75000/76000, seed4 0/122000/123000,
seed1 0/75000/76000, downloaded with curl from https://huggingface.co/EleutherAI/<repo>/resolve/<step>/pytorch_model.bin)."""
import sys, torch, itertools
D = sys.argv[1]
keys = ["gpt_neox.embed_in.weight", "gpt_neox.layers.5.attention.query_key_value.weight",
        "gpt_neox.layers.12.mlp.dense_h_to_4h.weight", "gpt_neox.layers.20.attention.dense.weight", "embed_out.weight"]
def load(name):
    sd = torch.load(f"{D}/{name}.bin", map_location="cpu", weights_only=True)
    return {k: sd[k].double().flatten() for k in keys}
def cos(a, b):
    return [round(float(torch.nn.functional.cosine_similarity(a[k], b[k], 0)), 3) for k in keys]
def nr(a, b):
    return [round(float(a[k].norm() / b[k].norm()), 2) for k in keys]
M = {}
for s, steps in (("seed3", (0, 75000, 76000)), ("seed4", (0, 122000, 123000)), ("seed1", (0, 75000, 76000))):
    for st in steps:
        M[(s, st)] = load(f"pythia-410m-{s}_step{st}")
print("tensors:", [k.replace("gpt_neox.", "") for k in keys])
for s, (a, b, c) in (("seed3", (0, 75000, 76000)), ("seed4", (0, 122000, 123000)), ("seed1", (0, 75000, 76000))):
    print(f"{s}: cos(step{b}, step{c}) = {cos(M[(s,b)], M[(s,c)])}   norm ratio step{c}/step{b} = {nr(M[(s,c)], M[(s,b)])}")
    print(f"{s}: cos(step{c}, step0)  = {cos(M[(s,c)], M[(s,a)])}")
    print(f"{s}: cos(step{b}, step0)  = {cos(M[(s,b)], M[(s,a)])}")
