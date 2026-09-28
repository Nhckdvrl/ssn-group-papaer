import time, torch, sys
from mg.sampler import load_pipe, sample
from mg.rules import cfg
pipe = load_pipe()
print("loaded", torch.cuda.max_memory_allocated()/1e9, flush=True)
prompts = ["a photo of four frisbees", "a dog to the right of a tie", "a red cube on top of a blue sphere", "a portrait of a woman wearing round glasses in a library"]
for B in [1, 4]:
    torch.cuda.synchronize(); t0 = time.time()
    r = sample(pipe, prompts[:B], list(range(B)), cfg(7.0), steps=30)
    torch.cuda.synchronize(); print("B", B, "sec", time.time() - t0, "mem", torch.cuda.max_memory_allocated()/1e9, flush=True)
for j, im in enumerate(r["images"]):
    im.save(f"{sys.argv[1]}/smoke_{j}.png")
g = r["geom"]
for k in ["norm_c", "norm_u", "norm_d", "cos_cu", "w_eff", "orth_rel"]:
    print(k, " ".join(f"{v:.3f}" for v in g[k][:, 0][::3]))
