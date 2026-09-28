import torch, numpy as np, sys
from transformers import AutoModelForCausalLM, AutoTokenizer
p = sys.argv[1]
tok = AutoTokenizer.from_pretrained(p)
m = AutoModelForCausalLM.from_pretrained(p, dtype=torch.bfloat16, device_map="cuda").eval()
print(m.config._attn_implementation, getattr(m.config, "sliding_window", None))
txt = "The quick brown fox jumps over the lazy dog. " + open("/home/xiang/ssn-group-papaer/README.md").read()[:3000]
ids = tok(txt, return_tensors="pt").input_ids.cuda()
with torch.no_grad():
    lg = m(input_ids=ids).logits.float()
nll = torch.nn.functional.cross_entropy(lg[0, :-1], ids[0, 1:], reduction="none")
print("short text len", ids.shape[1], "mean nll", nll.mean().item())
pk = np.load("/home/xiang/ssn-group-papaer/explorations/shape_olmo/data/pack_pg19.npz")["ids"][0]
print("decoded window head:", repr(tok.decode(pk[:60])))
for L in (512, 2048, 8192):
    x = torch.from_numpy(pk[:L]).long().cuda()[None]
    with torch.no_grad():
        lg = m(input_ids=x).logits.float()
    nll = torch.nn.functional.cross_entropy(lg[0, :-1], x[0, 1:], reduction="none")
    print("pg19 window0 L", L, "mean nll", nll.mean().item(), "first/last 512", nll[:511].mean().item(), nll[-511:].mean().item())
