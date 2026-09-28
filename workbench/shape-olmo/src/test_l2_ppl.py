import sys, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
p, trc = sys.argv[1], sys.argv[2] == "1"
tok = AutoTokenizer.from_pretrained(p, trust_remote_code=trc)
m = AutoModelForCausalLM.from_pretrained(p, dtype=torch.bfloat16, device_map="cuda", trust_remote_code=trc).eval()
print(type(m).__name__, type(m.model.layers[0].self_attn).__name__ if hasattr(m, "model") else "")
txt = open("/home/xiang/ssn-group-papaer/README.md").read()[:6000]
x = tok(txt, return_tensors="pt").input_ids[:, :1024].cuda()
with torch.no_grad():
    out = m(input_ids=x, attention_mask=torch.ones_like(x), use_cache=False)
print("mean NLL", torch.nn.functional.cross_entropy(out.logits[0, :-1].float(), x[0, 1:]).item())
