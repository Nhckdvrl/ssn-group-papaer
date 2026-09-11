"""Score the context-reliance probe for one checkpoint."""
import argparse, json, os, torch
from transformers import AutoTokenizer, AutoModelForCausalLM

TMPL = "{context}\n\nQuestion: {question}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--probe", default="data/probe.jsonl")
    ap.add_argument("--max_new", type=int, default=24)
    a = ap.parse_args()
    tokz = AutoTokenizer.from_pretrained(a.model)
    tokz.padding_side = "left"
    if tokz.pad_token is None: tokz.pad_token = tokz.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="auto",
        attn_implementation="sdpa").eval()
    rows = [json.loads(l) for l in open(a.probe)]
    recs, B = [], 8
    for i in range(0, len(rows), B):
        chunk = rows[i:i+B]
        prompts = [tokz.apply_chat_template(
            [{"role": "user", "content": TMPL.format(**r)}],
            tokenize=False, add_generation_prompt=True) for r in chunk]
        enc = tokz(prompts, return_tensors="pt", padding=True,
                   add_special_tokens=False).to(model.device)
        with torch.no_grad():
            g = model.generate(**enc, max_new_tokens=a.max_new, do_sample=False,
                               pad_token_id=tokz.pad_token_id)
        for r, o in zip(chunk, g):
            txt = tokz.decode(o[enc["input_ids"].shape[1]:],
                              skip_special_tokens=True).strip().lower()
            recs.append(dict(id=r["id"], atype=r["atype"], gen=txt,
                             ctx=r["counterfactual"].lower() in txt,
                             par=r["gold_parametric"].lower() in txt))
    n = len(recs)
    summ = dict(n=n,
                context_rate=sum(r["ctx"] and not r["par"] for r in recs)/n,
                parametric_rate=sum(r["par"] and not r["ctx"] for r in recs)/n,
                both=sum(r["ctx"] and r["par"] for r in recs)/n,
                neither=sum(not r["ctx"] and not r["par"] for r in recs)/n)
    os.makedirs(a.out, exist_ok=True)
    json.dump(summ, open(f"{a.out}/probe_summary.json", "w"), indent=1)
    with open(f"{a.out}/probe_raw.jsonl", "w") as w:
        for r in recs: w.write(json.dumps(r)+"\n")
    print(json.dumps(summ, indent=1))

if __name__ == "__main__":
    main()
