"""CPU audit for fixed-mask denominator contrasts; no model reruns."""
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]/"results/e152"


def read(p):return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()


def main():
    m=read(ROOT/"manifest.json");s=read(ROOT/"summary.json");plan=read(ROOT/"plan.json")
    assert m["status"]==s["status"]=="complete" and all(m["controls"].values())
    assert m["source_sha256"]==plan["source_sha256"]==read(ROOT/"self_test.json")["source_sha256"]
    assert sha(m["raw"]["path"])==m["raw"]["sha256"]
    with np.load(m["raw"]["path"]) as f:
        a=f["metrics"].astype(float);mask=f["suffix_valid"].copy();valid=f["valid"].copy();g=f["applied_gate_sum"].copy()
    assert a.shape==(2,11,64,512,4) and g.shape==(2,10,64,16)
    assert np.isfinite(a).all() and np.isfinite(g).all() and (g>=0).all()
    assert np.array_equal(mask,valid&(np.arange(512)[None,:]>=127)) and np.all(a[:,0,:,:,1:3]==0)
    values=np.einsum("st,bcstf->bcsf",mask.astype(float),a)/mask.sum(1)[None,None,:,None]
    penalty=values[:,:,:,0]-values[:,0:1,:,0];errors={}
    names=plan["mask_order"]
    for b,label in enumerate("AB"):
        for j,name in enumerate(names):
            row=s["sources"][label]["masks"][name]
            for r,rule in enumerate(("pool","full")):
                k=1+2*j+r
                errors[f"{label}_{name}_{rule}_NLL"]=abs(float(values[b,k,:,0].mean())-row[rule]["NLL"]["point"])
                errors[f"{label}_{name}_{rule}_delta"]=abs(float(penalty[b,k].mean())-row[rule]["delta_NLL"]["point"])
                errors[f"{label}_{name}_{rule}_KL"]=abs(float(values[b,k,:,1].mean())-row[rule]["native_to_variant_KL"]["point"])
            difference=values[b,2+2*j]-values[b,1+2*j]
            for field,index in (("NLL",0),("KL",1)):
                errors[f"{label}_{name}_rule_{field}"]=abs(float(difference[:,index].mean())-row["full_minus_pool"][field]["point"])
    for j,name in enumerate(names):
        lo,hi=1+2*j,2+2*j
        difference=(values[1,hi]-values[1,lo])-(values[0,hi]-values[0,lo])
        for field,index in (("NLL",0),("KL",1)):
            errors[f"{name}_DID_{field}"]=abs(float(difference[:,index].mean())-s["rule_difference_in_difference"][name][field]["point"])
    assert max(errors.values())<1e-10,errors
    budget=read(ROOT/"budget.json");assert all(v["status"]=="complete" for v in budget["attempts"])
    report={"status":"passed","CPU_only":True,"audit_source_sha256":sha(__file__),"raw_sha256":m["raw"]["sha256"],
        "max_point_error":max(errors.values()),"errors":errors,"suffix_targets":int(mask.sum()),
        "GPU_seconds":sum(v["gpu_seconds"] for v in budget["attempts"]),
        "scope":"Separate raw-array calculation by the same researcher, not independent L3 audit or new model observations."}
    (ROOT/"raw_verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","max_point_error","GPU_seconds")},indent=2))


if __name__=="__main__":main()
