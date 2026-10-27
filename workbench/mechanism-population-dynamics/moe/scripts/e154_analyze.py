"""E154 longitudinal profile summaries from parent and sealed descendant raw arrays."""
import argparse
import json
from pathlib import Path
import numpy as np
import e150_native as n
import e151_native as v

ROOT=n.WB/"results/e154"
CONDITIONS=("native","own_prefix","prefixA","prefixB","random0","random1","random2","routed_zero","shared_zero")


def reduce_targets(raw,valid):
    return np.einsum("st,cstf->csf",valid.astype(float),raw.astype(float))/valid.sum(1)[None,:,None]


def descendants():
    one=n.read(n.RESULT/"manifest.json")
    two=n.read(v.RESULT/"manifest.json")
    assert one["status"]==two["status"]=="complete"
    for m in (one,two):
        if n.sha(m["raw"]["path"])!=m["raw"]["sha256"]:
            raise ValueError("Sealed descendant raw changed")
    with np.load(one["raw"]["path"]) as f:
        prefixes=f["restricted_metrics"].copy()
        valid=f["valid"].copy()
        suffix=f["suffix_valid"].copy()
    with np.load(two["raw"]["path"]) as f:
        raw=f["metrics"].copy()
        assert np.array_equal(valid,f["valid"]) and np.array_equal(suffix,f["suffix_valid"])
    rows=[]
    for source,case in ((0,0),(1,15)):
        values=[raw[source,0],prefixes[source,case],prefixes[0,case],prefixes[1,case]]
        values.extend(raw[source,3+i] for i in range(3))
        values.extend((raw[source,1],raw[source,2]))
        rows.append(np.stack(values))
    return np.stack(rows),valid,suffix


def self_test():
    ab,valid,suffix=descendants()
    previous=n.read(v.RESULT/"summary.json")
    errors={}
    for b,label in enumerate("AB"):
        full=reduce_targets(ab[b],valid)
        tail=reduce_targets(ab[b],suffix)
        record=previous["sources"][label]
        for index,name in ((7,"routed_zero"),(8,"shared_zero")):
            actual=float((full[index,:,0]-full[0,:,0]).mean())
            expected=record["conditions"][name]["full_delta_NLL"]["point"]
            errors[f"{label}_{name}"]=abs(actual-expected)
        actual=float((tail[4:7,:,0].mean(0)-tail[0,:,0]).mean())
        errors[f"{label}_random"]=abs(actual-record["random_mean"]["suffix_delta_NLL"]["point"])
        actual=float((tail[4:7,:,0].mean(0)-tail[1,:,0]).mean())
        errors[f"{label}_selection"]=abs(actual-record["random_vs_prefix"][label]["random_mean_minus_prefix_NLL"]["point"])
    assert max(errors.values())<1e-12
    result={"status":"passed","CPU_only":True,"source_sha256":n.sha(__file__),"max_descendant_reconstruction_error":max(errors.values()),
            "checks":errors,"scope":"Reconstruction of sealed descendant contrasts before any public-parent model readings."}
    n.write(ROOT/"analysis_self_test.json",result)
    return result


def analyze():
    p=n.read(ROOT/"plan.json")
    m=n.read(ROOT/"manifest.json")
    if m["status"]!="complete" or n.sha(m["raw"]["path"])!=m["raw"]["sha256"]:
        raise ValueError("Complete sealed parent observations required")
    if n.sha(ROOT/"plan.json")!=m["plan_sha256"]:
        raise ValueError("Parent plan changed")
    if n.sha(n.RESULT/"manifest.json")!=p["E150_manifest_sha256"] or n.sha(v.RESULT/"manifest.json")!=p["E151_manifest_sha256"]:
        raise ValueError("Frozen descendant manifests changed")
    ab,valid,suffix=descendants()
    with np.load(m["raw"]["path"]) as f:
        parent=f["metrics"].copy()
        assert list(f["conditions"])==list(CONDITIONS)
        assert np.array_equal(valid,f["valid"]) and np.array_equal(suffix,f["suffix_valid"])
        masks=f["own_prefix_masks"].copy()
    assert parent.shape==(9,64,512,4) and np.isfinite(parent).all()
    assert masks.shape==(64,16,128) and masks[:,:,-1].all() and np.all(masks.sum(-1)==32)
    all_raw=np.concatenate((parent[None],ab),axis=0)
    stats=lambda x:n.input_stats(np.asarray(x),p["selected"],154001)
    result={"experiment":"E154","status":"complete","source_order":["P","A","B"],"conditions":list(CONDITIONS),"scopes":{},
            "analysis_source_sha256":n.sha(__file__),"parent_manifest_sha256":n.sha(ROOT/"manifest.json"),
            "scope":"One author-declared parent and two protocol descendants. Paired old-input file CIs, not model seeds, strict training causality, equivalence or intermediate dynamics."}
    for mask_name,mask in (("full",valid),("suffix",suffix)):
        values=np.stack([reduce_targets(raw,mask) for raw in all_raw])
        penalties=values[:,:,:,0]-values[:,0:1,:,0]
        profiles={}
        for i,label in enumerate(("P","A","B")):
            rows={}
            for j,name in enumerate(CONDITIONS):
                rows[name]={"NLL":stats(values[i,j,:,0]),"delta_NLL":stats(penalties[i,j]),
                            "native_to_variant_KL":stats(values[i,j,:,1]),"variant_to_native_KL":stats(values[i,j,:,2])}
            random=values[i,4:7].mean(0)
            profiles[label]={"conditions":rows,
                             "random_mean":{"NLL":stats(random[:,0]),"delta_NLL":stats(random[:,0]-values[i,0,:,0]),
                                            "KL":stats(random[:,1])},
                             "own_prefix_selection_advantage":{"NLL":stats(random[:,0]-values[i,1,:,0]),
                                                               "KL":stats(random[:,1]-values[i,1,:,1])}}
        changes={}
        for child,label in ((1,"A_minus_P"),(2,"B_minus_P")):
            rows={}
            for j,name in enumerate(CONDITIONS):
                rows[name]={"NLL":stats(values[child,j,:,0]-values[0,j,:,0]),
                            "delta_NLL":stats(penalties[child,j]-penalties[0,j]),
                            "KL":stats(values[child,j,:,1]-values[0,j,:,1])}
            rows["random_mean"]={"delta_NLL":stats(penalties[child,4:7].mean(0)-penalties[0,4:7].mean(0)),
                                 "KL":stats(values[child,4:7,:,1].mean(0)-values[0,4:7,:,1].mean(0))}
            rows["own_prefix_selection_advantage"]={
                "NLL":stats((values[child,4:7,:,0].mean(0)-values[child,1,:,0])-(values[0,4:7,:,0].mean(0)-values[0,1,:,0])),
                "KL":stats((values[child,4:7,:,1].mean(0)-values[child,1,:,1])-(values[0,4:7,:,1].mean(0)-values[0,1,:,1]))}
            changes[label]=rows
        result["scopes"][mask_name]={"profiles":profiles,"descendant_minus_parent":changes}
    n.write(ROOT/"summary.json",result)
    return {"status":"complete","suffix_profiles":{label:{name:result["scopes"]["suffix"]["profiles"][label]["conditions"][name]["delta_NLL"]
              for name in ("own_prefix","routed_zero","shared_zero")} for label in ("P","A","B")}}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("self-test","analyze"))
    args=parser.parse_args()
    print(json.dumps(self_test() if args.mode=="self-test" else analyze(),indent=2),flush=True)
