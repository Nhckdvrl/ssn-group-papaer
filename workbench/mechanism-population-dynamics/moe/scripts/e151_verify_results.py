"""CPU audit of E151 metrics and fixed-probe contrasts, without model reruns."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/"results/e151"


def read(path):return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()


def mean_targets(a,mask):
    return np.einsum("st,stf->sf",mask.astype(float),a.astype(float))/mask.sum(1)[:,None]


def main():
    manifest=read(ROOT/"manifest.json");s=read(ROOT/"summary.json");plan=read(ROOT/"plan.json")
    assert manifest["status"]==s["status"]=="complete" and all(manifest["controls"].values())
    assert manifest["source_sha256"]==plan["source_sha256"]==read(ROOT/"self_test.json")["source_sha256"]
    raw=manifest["raw"];assert sha(raw["path"])==raw["sha256"]
    masks=plan["random_masks"];assert sha(masks["path"])==masks["sha256"]
    with np.load(masks["path"]) as f:assert f["masks"].shape==(3,64,16,128) and np.all(f["masks"].sum(-1)==32) and f["masks"][:,:,:,-1].all()
    with np.load(raw["path"]) as f:
        values=f["metrics"].copy();valid=f["valid"].copy();suffix=f["suffix_valid"].copy();conditions=f["conditions"].tolist()
    assert values.shape==(2,6,64,512,4) and np.isfinite(values).all() and np.all(values[:,0,:,:,1:3]==0)
    full=np.stack([[mean_targets(v,valid) for v in model] for model in values])
    suf=np.stack([[mean_targets(v,suffix) for v in model] for model in values])
    previous=read(ROOT.parent/"e150/manifest.json");assert sha(previous["raw"]["path"])==previous["raw"]["sha256"]
    with np.load(previous["raw"]["path"]) as f:
        prefixes=np.stack([[mean_targets(f["restricted_metrics"][p,i],suffix) for p in range(2)] for i in (0,15)])
        for source,i in enumerate((0,15)):assert np.array_equal(values[source,0,:,:,0],f["metrics"][i,:,:,0,0])
    errors={}
    for source,name in enumerate("AB"):
        row=s["sources"][name]
        for i,condition in enumerate(conditions):
            target=row["conditions"][condition]
            for label,v in (("full_NLL",full[source,i,:,0]),("full_delta_NLL",full[source,i,:,0]-full[source,0,:,0]),
                            ("full_KL",full[source,i,:,1]),("suffix_delta_NLL",suf[source,i,:,0]-suf[source,0,:,0]),("suffix_KL",suf[source,i,:,1])):
                errors[name+"_"+condition+"_"+label]=abs(float(v.mean())-target[label]["point"])
        for p,selector in enumerate("AB"):
            for field,k in (("random_mean_minus_prefix_NLL",0),("random_mean_minus_prefix_KL",1)):
                value=suf[source,3:,:,k].mean(0)-prefixes[source,p,:,k]
                errors[name+"_"+selector+"_"+field]=abs(float(value.mean())-row["random_vs_prefix"][selector][field]["point"])
    assert max(errors.values())<1e-10,errors
    budget=read(ROOT/"budget.json");assert all(a["status"]=="complete" for a in budget["attempts"])
    result={"status":"passed","CPU_only":True,"audit_source_sha256":sha(__file__),"raw_sha256":raw["sha256"],
        "max_point_error":max(errors.values()),"point_errors":errors,"source_native_NLL_exact_E150":True,
        "full_targets":int(valid.sum()),"suffix_targets":int(suffix.sum()),"random_draws":3,
        "GPU_seconds":sum(x["gpu_seconds"] for x in budget["attempts"]),
        "scope":"Same researcher, separate raw-array calculation; no independent L3 audit, training seeds or new measurements."}
    (ROOT/"raw_verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("status","max_point_error","GPU_seconds")},indent=2))


if __name__=="__main__":main()
