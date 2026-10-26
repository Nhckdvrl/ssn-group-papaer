"""CPU raw-array audit with a separate tensor-axis implementation of contrasts."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/"results/e150"


def sha(path):
    with Path(path).open("rb") as stream:return hashlib.file_digest(stream,"sha256").hexdigest()


def read(path):return json.loads(Path(path).read_text())


def average_targets(array,mask):
    # Keep the actual sequence denominator; padding is never a score or sample.
    return np.einsum("st,st...->s...",mask.astype(float),array.astype(float))/mask.sum(1).reshape((-1,)+(1,)*(array.ndim-2))


def tensor_contrasts(sequence_values):
    cube=sequence_values.reshape(2,2,2,2,64)
    effects=[float((np.take(cube,1,axis=i)-np.take(cube,0,axis=i)).mean()) for i in range(4)]
    gr=cube[:,1,1,:,:]-cube[:,0,1,:,:]-cube[:,1,0,:,:]+cube[:,0,0,:,:]
    rs=cube[:,:,1,1,:]-cube[:,:,0,1,:]-cube[:,:,1,0,:]+cube[:,:,0,0,:]
    dense=cube[1,1,1,1]-cube[0,1,1,1]-cube[1,0,0,0]+cube[0,0,0,0]
    return effects,[-float(v.mean())/2 for v in (gr,rs,dense)]


def main():
    manifest=read(ROOT/"manifest.json");summary=read(ROOT/"summary.json");plan=read(ROOT/"plan.json")
    assert manifest["status"]==summary["status"]=="complete"
    assert manifest["source_sha256"]==read(ROOT/"preflight.json")["source_sha256"]==read(ROOT/"self_test.json")["source_sha256"]
    assert all(manifest["controls"].values())
    raw=manifest["raw"];assert sha(raw["path"])==raw["sha256"]
    with np.load(raw["path"]) as f:
        full=f["metrics"].copy();pruned=f["restricted_metrics"].copy()
        valid=f["valid"].copy();suffix=f["suffix_valid"].copy();keeps=f["prefix_keeps"].copy()
        coverage=f["routing_coverage"].copy();cases=f["cases"].copy()
    assert full.shape==(16,64,512,2,4) and pruned.shape==(2,16,64,512,4)
    assert np.isfinite(full).all() and np.isfinite(pruned).all() and np.isfinite(coverage).all()
    with np.load(plan["path"]) as source:assert np.array_equal(valid,source["held_mask"])
    assert np.array_equal(suffix,valid&(np.arange(512)[None,:]>=127))
    assert keeps.shape==(2,64,16,128) and np.all(keeps.sum(-1)==32) and keeps[:,:,:,-1].all()
    assert np.array_equal(full[...,0,0],full[...,1,0])
    assert np.all(full[0,:,:,0,1:3]==0) and np.all(full[-1,:,:,1,1:3]==0)
    full_mean=np.stack([average_targets(v,valid) for v in full])
    suffix_mean=np.stack([average_targets(v,suffix) for v in full])
    restricted=np.stack([[average_targets(v,suffix) for v in policy] for policy in pruned])
    names=["".join("AB"[int(c)] for c in case) for case in cases]
    factors=("dense_backbone","all_routers","routed_experts","shared_experts")
    keys=("router_x_routed","routed_x_shared","dense_x_complete_MoE")
    errors={}
    for i,name in enumerate(names):
        errors[name+"_full_NLL"]=abs(float(full_mean[i,:,0,0].mean())-summary["cases"][name]["nll"]["point"])
        for policy,selector in enumerate("AB"):
            point=float((restricted[policy,i,:,0]-suffix_mean[i,:,0,0]).mean())
            errors[selector+"_"+name+"_pruning_NLL"]=abs(point-summary["restriction"]["selectors"][selector]["cases"][name]["pruning_delta_nll"]["point"])
    for policy,selector in enumerate("AB"):
        row=summary["restriction"]["selectors"][selector]
        for metric,values,effect_key,coupling_key in (
            ("NLL",restricted[policy,:,:,0]-suffix_mean[:,:,0,0],"factor_effect_on_pruning_penalty","pruning_penalty_coupling"),
            ("KL",restricted[policy,:,:,1],"factor_effect_on_full_to_restricted_KL","full_to_restricted_KL_coupling")):
            effects,costs=tensor_contrasts(values)
            for i,factor in enumerate(factors):
                errors[selector+"_"+metric+"_"+factor]=abs(effects[i]-row[effect_key][factor+"_B_minus_A"]["point"])
            for i,key in enumerate(keys):
                field="pairing_cost" if i==2 else "mean_pairing_cost"
                errors[selector+"_"+metric+"_"+key]=abs(costs[i]-row[coupling_key][key][field]["point"])
    sidecar=manifest["normalizer_observation"]["raw"];assert sha(sidecar["path"])==sidecar["sha256"]
    with np.load(sidecar["path"]) as f:normal=f["values"].astype(float)
    assert normal.shape==(2,16,64,16,2) and np.isfinite(normal).all()
    jensen=normal[...,0]*normal[...,1]-1
    assert normal[...,0].min()>0 and normal[...,0].max()<1+1e-6
    assert normal[...,1].min()>1-1e-6 and jensen.min()>-1e-5
    assert max(errors.values())<1e-10,errors
    budget=read(ROOT/"budget.json");assert all(a["status"]=="complete" for a in budget["attempts"])
    report={"status":"passed","CPU_only":True,"audit_source_sha256":sha(__file__),
        "raw_sha256":raw["sha256"],"normalizer_raw_sha256":sidecar["sha256"],"max_point_or_contrast_error":max(errors.values()),
        "errors":errors,"scored_targets":{"full_per_cell":int(valid.sum()),"suffix_per_restricted_cell":int(suffix.sum())},
        "normalizer_Jensen_min_gap":float(jensen.min()),"coverage_numeric_range":[float(coverage.min()),float(coverage.max())],
        "GPU_seconds":sum(a["gpu_seconds"] for a in budget["attempts"]),
        "scope":"Same researcher, separate raw-array/tensor-axis calculation and invariant checks. No new model runs, no independent L3 audit or evidence-grade promotion."}
    (ROOT/"raw_verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","max_point_or_contrast_error","scored_targets","GPU_seconds")},indent=2))


if __name__=="__main__":main()
