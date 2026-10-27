"""E154 CPU array audit without model reruns or the analysis reduction helper."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results/e154"
NAMES=("native","own_prefix","prefixA","prefixB","random0","random1","random2","routed_zero","shared_zero")


def read(p):
    return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def main():
    m=read(OUT/"manifest.json")
    summary=read(OUT/"summary.json")
    plan=read(OUT/"plan.json")
    assert m["status"]==summary["status"]=="complete" and all(m["controls"].values())
    assert m["source_sha256"]==plan["source_sha256"]==read(OUT/"self_test.json")["source_sha256"]
    assert sha(m["raw"]["path"])==m["raw"]["sha256"]
    with np.load(m["raw"]["path"]) as f:
        parent=f["metrics"].copy()
        valid=f["valid"].copy()
        tail=f["suffix_valid"].copy()
        masks=f["own_prefix_masks"].copy()
    assert parent.shape==(9,64,512,4) and np.isfinite(parent).all()
    assert np.all(parent[0,:,:,1:3]==0)
    assert masks.shape==(64,16,128) and masks[...,-1].all() and np.all(masks.sum(-1)==32)
    assert np.array_equal(tail,valid&(np.arange(512)[None,:]>=127))
    cube=read(ROOT/"results/e150/manifest.json")
    needs=read(ROOT/"results/e151/manifest.json")
    for x in (cube,needs):
        assert sha(x["raw"]["path"])==x["raw"]["sha256"]
    with np.load(cube["raw"]["path"]) as f:
        prefix=f["restricted_metrics"].copy()
        assert np.array_equal(valid,f["valid"]) and np.array_equal(tail,f["suffix_valid"])
    with np.load(needs["raw"]["path"]) as f:
        previous=f["metrics"].copy()
        assert np.array_equal(valid,f["valid"]) and np.array_equal(tail,f["suffix_valid"])
    descendants=np.empty((2,9,64,512,4),np.float32)
    for source,corner in ((0,0),(1,15)):
        descendants[source,0]=previous[source,0]
        descendants[source,1]=prefix[source,corner]
        descendants[source,2]=prefix[0,corner]
        descendants[source,3]=prefix[1,corner]
        descendants[source,4:7]=previous[source,3:6]
        descendants[source,7]=previous[source,1]
        descendants[source,8]=previous[source,2]
    raw=np.concatenate((parent[None],descendants),axis=0)
    errors={}
    for scope,mask in (("full",valid),("suffix",tail)):
        values=np.empty((3,9,64,3))
        for source in range(3):
            for condition in range(9):
                for seq in range(64):
                    values[source,condition,seq]=raw[source,condition,seq,mask[seq],:3].astype(float).mean(axis=0)
        delta=values[:,:,:,0]-values[:,0:1,:,0]
        profiles=summary["scopes"][scope]["profiles"]
        for source,label in enumerate(("P","A","B")):
            for condition,name in enumerate(NAMES):
                record=profiles[label]["conditions"][name]
                for field,column in (("NLL",0),("native_to_variant_KL",1),("variant_to_native_KL",2)):
                    errors[f"{scope}/{label}/{name}/{field}"]=abs(float(values[source,condition,:,column].mean())-record[field]["point"])
                errors[f"{scope}/{label}/{name}/penalty"]=abs(float(delta[source,condition].mean())-record["delta_NLL"]["point"])
            random=values[source,4:7].mean(axis=0)
            errors[f"{scope}/{label}/selection"]=abs(float((random[:,0]-values[source,1,:,0]).mean())-profiles[label]["own_prefix_selection_advantage"]["NLL"]["point"])
        changes=summary["scopes"][scope]["descendant_minus_parent"]
        for source,label in ((1,"A_minus_P"),(2,"B_minus_P")):
            for condition,name in enumerate(NAMES):
                errors[f"{scope}/{label}/{name}/penalty"]=abs(float((delta[source,condition]-delta[0,condition]).mean())-changes[label][name]["delta_NLL"]["point"])
    assert max(errors.values())<1e-10
    ledger=read(OUT/"budget.json")
    assert all(x["status"]=="complete" for x in ledger["attempts"])
    result={"status":"passed","CPU_only":True,"source_sha256":sha(__file__),"raw_sha256":m["raw"]["sha256"],
            "max_point_error":max(errors.values()),"contrasts_checked":len(errors),"errors":errors,
            "GPU_seconds":sum(x["gpu_seconds"] for x in ledger["attempts"]),
            "scope":"Separate raw-array implementation by the same researcher; no independent L3 audit, model seeds or new observations."}
    (OUT/"raw_verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("status","max_point_error","contrasts_checked","GPU_seconds")},indent=2))


if __name__=="__main__":
    main()
