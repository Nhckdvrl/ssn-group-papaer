"""E16 stage 0 POST-HOC (round 9, 2026-11-29): solve rate on the 44 evidence problems, outcome breakdown of disc_ref and of disc_cand on the correct reference, and paired (same instance) problem-clustered bootstrap differences.
Usage: python3 e16f_round9_breakdown.py <dir with fscored/> (expects ../../f11/fdata/ev_set.jsonl relative to it, as in the archive layout)
"""
import json, collections, random, statistics, sys
D=sys.argv[1]
M=["c15","c7","qwen","cure","r1","tcs"]
ev=set(json.loads(l)["id"] for l in open(D+"/../../f11/fdata/ev_set.jsonl"))
def load(p): return [json.loads(l) for l in open(p)]
S={t:load(f"{D}/solve_{t}.jsonl") for t in M}
R={t:load(f"{D}/ev_{t}.jsonl") for t in M}
print("== solve pass: all159 / ev44 ; finish=length frac on evidence tasks; median tokens disc_ref / disc_cand")
for t in M:
    a=S[t]; b=[r for r in a if r["pid"] in ev]
    dr=[r for r in R[t] if r["task"]=="disc_ref"]; dc=[r for r in R[t] if r["task"]=="disc_cand"]
    trunc=sum(r["finish"]=="length" for r in R[t] if r["task"]!="judge")/sum(1 for r in R[t] if r["task"]!="judge")
    print(t, "%.3f / %.3f"%(sum(bool(r.get("pass_all")) for r in a)/len(a), sum(bool(r.get("pass_all")) for r in b)/len(b)),
          "trunc %.3f"%trunc, statistics.median(r["n_tokens"] for r in dr), statistics.median(r["n_tokens"] for r in dc))
print("\n== disc_ref breakdown: no input given / given-but-invalid / valid-no-diff / success  (by source)")
for t in M:
    for src in ("external","mutant"):
        rs=[r for r in R[t] if r["task"]=="disc_ref" and r["source"]==src]; n=len(rs)
        ng=sum(not r.get("gave_input") for r in rs); trn=sum((not r.get("gave_input")) and r["finish"]=="length" for r in rs)
        inv=sum(r.get("gave_input") and not r.get("valid") for r in rs)
        vn=sum(bool(r.get("valid")) and not r.get("success") for r in rs); su=sum(bool(r.get("success")) for r in rs)
        print(t,src,n,"noinput %.2f (trunc %.2f) invalid %.2f valid_nodiff %.2f success %.2f"%(ng/n,trn/n,inv/n,vn/n,su/n))
print("\n== disc_cand on the CORRECT reference: said CORRECT / gave an accusing input / neither (trunc)")
for t in M:
    rs=[r for r in R[t] if r["task"]=="disc_cand" and r["label"]=="correct"]; n=len(rs)
    sc=sum(r.get("said_correct") and not r.get("gave_input") for r in rs)
    gi=sum(bool(r.get("gave_input")) for r in rs); both=sum(bool(r.get("said_correct")) and bool(r.get("gave_input")) for r in rs)
    nei=sum((not r.get("said_correct")) and not r.get("gave_input") for r in rs)
    tr=sum((not r.get("said_correct")) and not r.get("gave_input") and r["finish"]=="length" for r in rs)
    giv=sum(bool(r.get("gave_input")) and bool(r.get("valid")) for r in rs)
    print(t,n,"CORRECT-only %.2f  accuse(input) %.2f [valid %.2f] both %.2f  neither %.2f (trunc %.2f)"%(sc/n,gi/n,giv/n,both/n,nei/n,tr/n))
print("\n== disc_cand on bugs: success (gave distinguishing input) / said CORRECT / neither")
for t in M:
  for src in ("external","mutant"):
    rs=[r for r in R[t] if r["task"]=="disc_cand" and r["source"]==src]; n=len(rs)
    print(t,src,n,"success %.2f saidCORRECT %.2f gave_input %.2f valid %.2f"%(sum(bool(r.get("success")) for r in rs)/n,sum(bool(r.get("said_correct")) and not r.get("gave_input") for r in rs)/n,sum(bool(r.get("gave_input")) for r in rs)/n,sum(bool(r.get("valid")) for r in rs)/n))
# paired bootstrap
def key(r): return (r["pid"],r["inst"],r["sample"])
def paired(a,b,task,src,f,label=None,B=4000):
    A={key(r):r for r in R[a] if r["task"]==task and r["source"]==src and (label is None or r["label"]==label)}
    Bm={key(r):r for r in R[b] if r["task"]==task and r["source"]==src and (label is None or r["label"]==label)}
    ks=sorted(set(A)&set(Bm)); by=collections.defaultdict(list)
    for k in ks: by[k[0]].append(f(A[k])-f(Bm[k]))
    ps=sorted(by); rng=random.Random(0); vals=[]
    for _ in range(B):
        xs=[x for p in (rng.choice(ps) for _ in ps) for x in by[p]]; vals.append(sum(xs)/len(xs))
    vals.sort(); d=sum(x for p in ps for x in by[p])/len(ks)
    return len(ks),len(ps),d,vals[int(.025*B)],vals[int(.975*B)-1]
succ=lambda r: float(bool(r.get("success"))); val=lambda r: float(bool(r.get("valid")))
acc=lambda r: float(bool(r.get("gave_input")))
print("\n== paired differences (same instance & sample), problem-clustered bootstrap 95%")
for a,b in (("tcs","r1"),("cure","qwen"),("r1","qwen"),("c7","qwen"),("tcs","c7")):
    for task,src,f,nm,lab in (("disc_ref","external",succ,"ref succ",None),("disc_ref","mutant",succ,"ref succ",None),
                         ("disc_ref","external",val,"ref valid",None),("disc_ref","mutant",val,"ref valid",None),
                         ("disc_cand","external",succ,"noref succ",None),("disc_cand","mutant",succ,"noref succ",None),
                         ("disc_cand","ref",acc,"noref accuse-correct",None)):
        n,p,d,lo,hi=paired(a,b,task,src,f,lab)
        print(f"{a}-{b} {nm:20s} {src:8s} n={n} P={p} diff {d:+.3f} [{lo:+.3f},{hi:+.3f}]")
