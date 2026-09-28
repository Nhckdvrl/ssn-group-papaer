"""Audit: each family must (a) change the logits, (b) restore them exactly on exit."""
import sys, pathlib, torch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from transformers import AutoModelForCausalLM, AutoTokenizer
from src import interventions

M = "Qwen/Qwen2.5-0.5B-Instruct"
tok = AutoTokenizer.from_pretrained(M)
m = AutoModelForCausalLM.from_pretrained(M, dtype=torch.float32).eval()
ids = tok("The capital of France is", return_tensors="pt")
with torch.no_grad(): base = m(**ids).logits.clone()
for fam, lvl in (("readout", 0.5), ("prune", 0.5), ("quant", 3)):
    with torch.no_grad(), interventions.make(m, fam, lvl):
        got = m(**ids).logits.clone()
    with torch.no_grad(): after = m(**ids).logits
    print(f"{fam:<9} level={lvl:<5} changed: max|d|={float((got-base).abs().max()):9.3f}"
          f"   restored: max|d|={float((after-base).abs().max()):.2e}")
