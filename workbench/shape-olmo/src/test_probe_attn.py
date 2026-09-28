"""Check probe_attn's recomputed last-row attention against eager output_attentions on a short item."""
import sys, torch
sys.path.insert(0, "src")
from probe_order import items
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.models.olmo_hybrid.modeling_olmo_hybrid import apply_rotary_pos_emb
path = sys.argv[1]
tok = AutoTokenizer.from_pretrained(path)
m = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32, device_map="cuda", attn_implementation="eager").eval()
it = [x for x in items(tok) if x["task"] == "reassign" and x["n"] == 2 and x["gap"] == 4][0]
ids = tok(it["text"], add_special_tokens=False).input_ids; L = len(ids)
cap = {}
i = [j for j, t in enumerate(m.config.layer_types) if t == "full_attention"][1]
att = m.model.layers[i].self_attn
att.q_norm.register_forward_hook(lambda mod, a, o: cap.__setitem__("q", o))
att.k_norm.register_forward_hook(lambda mod, a, o: cap.__setitem__("k", o))
with torch.no_grad():
    out = m(input_ids=torch.tensor(ids, device="cuda")[None], output_attentions=True)
A = [a for a in out.attentions if a is not None]
full = [j for j, t in enumerate(m.config.layer_types) if t == "full_attention"]
print("len(attentions)", len(out.attentions), "non-None", len(A))
ref = (out.attentions[i] if len(out.attentions) == len(m.config.layer_types) and out.attentions[i] is not None else A[full.index(i)])[0, :, -1]
cfg = m.config; hd = cfg.head_dim if getattr(cfg, "head_dim", None) else cfg.hidden_size // cfg.num_attention_heads
H, KV = cfg.num_attention_heads, cfg.num_key_value_heads
q = cap["q"].view(1, L, H, hd).transpose(1, 2); k = cap["k"].view(1, L, KV, hd).transpose(1, 2)
if m.model.rotary_emb is not None:
    q, k = apply_rotary_pos_emb(q, k, *m.model.rotary_emb(q, torch.arange(L, device="cuda")[None]))
k = k.repeat_interleave(H // KV, 1)
p = torch.softmax((q[0, :, -1:] @ k[0].transpose(-1, -2))[:, 0] * hd ** -0.5, -1)
print("layer", i, "L", L, "max|recomputed - eager|", (p - ref).abs().max().item(), "rotary", m.model.rotary_emb is not None)
