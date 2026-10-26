"""Frozen E150 statistics plus the separately sealed normalizer observations."""
import json
import numpy as np
import e150_native as n


def main():
    n.analyze()
    manifest=n.read(n.RESULT/"manifest.json")
    report=n.read(n.RESULT/"summary.json")
    plan=n.read(n.RESULT/"plan.json")
    observer=manifest["normalizer_observation"]
    raw=observer["raw"]
    if observer["status"]!="complete" or n.sha(raw["path"])!=raw["sha256"]: raise ValueError("Sealed normalizer sidecar required")
    with np.load(raw["path"]) as f: values=f["values"].copy()
    if values.shape!=(2,16,64,16,2): raise ValueError("Normalizer axes differ")
    stats=lambda x:n.input_stats(np.asarray(x),plan["selected"],150001)
    with np.load(manifest["raw"]["path"]) as f:
        kl=np.stack([[n.data.masked_mean(v.astype(float),f["suffix_valid"])[:,1]
                      for v in policy] for policy in f["restricted_metrics"]])
    for policy,selector in enumerate("AB"):
        for index,case in enumerate(n.CASES):
            key="".join("AB"[c] for c in case)
            target=report["restriction"]["selectors"][selector]["cases"][key]
            target["mean_layer_retained_full_router_probability"]=stats(values[policy,index,:,:,0].mean(-1))
            target["mean_layer_inverse_retained_probability"]=stats(values[policy,index,:,:,1].mean(-1))
        ys={case:kl[policy,i] for i,case in enumerate(n.CASES)}
        effects={}
        for axis,factor in enumerate(n.FACTORS):
            flips=[n.interaction(ys,(axis,),fixed) for fixed in n.itertools.product(range(2),repeat=3)]
            effects[factor+"_B_minus_A"]=stats(np.mean(flips,axis=0))
        output=report["restriction"]["selectors"][selector]
        output["factor_effect_on_full_to_restricted_KL"]=effects
        coupling={}
        for axes,label in (((1,2),"router_x_routed"),((2,3),"routed_x_shared")):
            value=np.mean([n.interaction(ys,axes,fixed) for fixed in n.itertools.product(range(2),repeat=2)],axis=0)
            coupling[label]={"mean_interaction":stats(value),"mean_pairing_cost":stats(-value/2)}
        value=ys[(1,1,1,1)]-ys[(0,1,1,1)]-ys[(1,0,0,0)]+ys[(0,0,0,0)]
        coupling["dense_x_complete_MoE"]={"interaction":stats(value),"pairing_cost":stats(-value/2)}
        output["full_to_restricted_KL_coupling"]=coupling
    report["restriction"]["native_own_selector_B_minus_A_full_to_restricted_KL"]=stats(kl[1,-1]-kl[0,0])
    report["normalizer_scope"]="FP32 full routed softmax before BF16 cast, shared excluded; read-only conditional scale diagnostic, not a mechanism claim or a linear NLL correction."
    report["analysis_execution"]={"analysis_wrapper_sha256":n.sha(__file__),"original_analyzer_sha256":n.sha(n.__file__),
        "observer_execution_sha256":observer["execution_adapter_sha256"],"model_math_unchanged":True,
        "core_stats_and_condition_set_unchanged":True}
    n.write(n.RESULT/"summary.json",report)
    print(json.dumps({"status":"complete","native_NLL":[report["cases"][k]["nll"]["point"] for k in ("AAAA","BBBB")],
        "full_primary":report["primary"],"own_selector_B_minus_A_pruning_penalty":report["restriction"]["native_own_selector_B_minus_A_pruning_penalty"],
        "factor_effects_on_pruning":{s:r["factor_effect_on_pruning_penalty"] for s,r in report["restriction"]["selectors"].items()}},indent=2))


if __name__=="__main__":main()
