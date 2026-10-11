import sys, glob, json, statistics as st
sys.path.insert(0,"src")
from nq_extract import extract
import pyarrow.parquet as pq
from transformers import AutoTokenizer

TOKID = "princeton-nlp/Llama-3-8B-ProLong-512k-Base"
tokz = AutoTokenizer.from_pretrained(TOKID)
files = sorted(glob.glob("/home/xiang/.cache/huggingface/hub/datasets--google-research-datasets--natural_questions/snapshots/*/default/train-*.parquet"))
print(len(files),"shards", flush=True)
seen=0; kept=[]
reasons={}
for f in files:
    for b in pq.ParquetFile(f).iter_batches(batch_size=64):
        for r in b.to_pylist():
            seen+=1
            e=extract(r)
            if e is None: continue
            e["tok_support"]=len(tokz(e["support"],add_special_tokens=False)["input_ids"])
            e["tok_page"]=len(tokz(e["page"],add_special_tokens=False)["input_ids"])
            kept.append(e)
print(f"seen={seen} kept={len(kept)} yield={len(kept)/seen:.3f}")
sup=[e["tok_support"] for e in kept]; pg=[e["tok_page"] for e in kept]
def q(v,p): 
    v=sorted(v); return v[int(p*(len(v)-1))]
for name,v in [("support",sup),("page",pg)]:
    print(f"{name:8s} median={st.median(v):7.0f} mean={st.mean(v):8.0f} p10={q(v,.1):6.0f} p25={q(v,.25):6.0f} p75={q(v,.75):7.0f} p90={q(v,.9):8.0f} max={max(v)}")
import collections
for thr in [2000,4000,8000,16000,32000]:
    print(f"page >= {thr:6d}: {sum(1 for x in pg if x>=thr):5d} ({sum(1 for x in pg if x>=thr)/len(pg):.2%})")
for thr in [256,512,1024]:
    print(f"support <= {thr:5d}: {sum(1 for x in sup if x<=thr):5d} ({sum(1 for x in sup if x<=thr)/len(sup):.2%})")
both=[e for e in kept if e["tok_support"]<=512 and e["tok_page"]>=8000 and e["tok_page"]<=32000]
print(f"\nBOTH (support<=512, 8000<=page<=32000): {len(both)} = {len(both)/seen:.3%} of raw examples")
json.dump(kept,open("data/audit_sample.json","w"))
