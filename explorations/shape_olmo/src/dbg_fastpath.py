"""Compare olmo_hybrid NLL with transformers' torch GDN fallback vs forced fla fast path."""
import sys, numpy as np, torch
mode = sys.argv[2]
if mode == "fla":
    import transformers.utils.import_utils as iu
    iu.is_flash_linear_attention_available = lambda: True
    import transformers.utils as tu
    tu.is_flash_linear_attention_available = lambda: True
from transformers import AutoModelForCausalLM
import transformers.models.olmo_hybrid.modeling_olmo_hybrid as mh
print("fast path:", mh.is_fast_path_available, mh.chunk_gated_delta_rule)
m = AutoModelForCausalLM.from_pretrained(sys.argv[1], dtype=torch.bfloat16, device_map="cuda").eval()
for dom in ("python", "pg19"):
    x = torch.from_numpy(np.load(f"data/pack_{dom}.npz")["ids"][0]).long().cuda()[None]
    with torch.no_grad():
        lg = m(input_ids=x).logits[0, :-1].float()
    nll = torch.nn.functional.cross_entropy(lg, x[0, 1:], reduction="none")
    print(mode, dom, "window0 nll", nll.mean().item(), "first512", nll[:511].mean().item())
