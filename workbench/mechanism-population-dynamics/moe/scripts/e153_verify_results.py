"""CPU-only E153 audit: scoring axes, masks, pairing and reported point contrasts."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]/"results/e153"


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def mean_by_subject(values,subjects):
    return float(np.mean([np.mean(values[subjects==x]) for x in np.unique(subjects)]))


def main():
    manifest=read(ROOT/"manifest.json")
    summary=read(ROOT/"summary.json")
    plan=read(ROOT/"plan.json")
    data=read(ROOT/"data_plan.json")
    selectors=read(ROOT/"selectors.json")
    assert manifest["status"]==summary["status"]=="complete"
    assert all(manifest["controls"].values())
    assert manifest["source_sha256"]==plan["source_sha256"]==read(ROOT/"self_test.json")["source_sha256"]
    assert sha(ROOT/"plan.json")==manifest["plan_sha256"]
    assert sha(manifest["raw"]["path"])==manifest["raw"]["sha256"]
    assert sha(ROOT/"selectors.json")==manifest["selectors_sha256"]
    assert sha(selectors["mask"]["path"])==selectors["mask"]["sha256"]
    assert sha(data["data"]["path"])==data["data"]["sha256"]
    with np.load(manifest["raw"]["path"]) as f:
        a={k:f[k].copy() for k in f.files}
    with np.load(data["data"]["path"]) as f:
        inputs={k:f[k].copy() for k in f.files}
    with np.load(selectors["mask"]["path"]) as f:
        masks=f["masks"].copy()
        probabilities=f["mean_probabilities"].copy()
    assert masks.shape==(2,2,16,128) and masks.dtype==bool
    assert np.all(masks.sum(-1)==32) and masks[...,-1].all()
    assert probabilities.shape==(2,2,16,127) and np.isfinite(probabilities).all()
    assert np.allclose(probabilities.sum(-1),1,atol=2e-7)
    for source in range(2):
        for topic in range(2):
            for layer in range(16):
                expected=np.zeros(128,bool)
                expected[np.argsort(-probabilities[source,topic,layer],kind="stable")[:31]]=True
                expected[-1]=True
                assert np.array_equal(expected,masks[source,topic,layer])
    ll=a["candidate_loglikelihood"]
    gold=a["gold"]
    topics=a["subject"]
    tokens=a["answer_tokens"]
    chars=a["answer_chars"]
    kl=a["first_answer_token_KL"]
    assert ll.shape==(4,3,128,4) and np.isfinite(ll).all() and (ll<=0).all()
    assert kl.shape==(4,3,128) and np.isfinite(kl).all() and (kl>=-1e-6).all()
    assert np.all(kl[:,0]==0)
    assert np.array_equal(np.bincount(topics),[64,64])
    for field in ("gold","subject","answer_tokens","answer_chars"):
        assert np.array_equal(a[field],inputs[field])
    assert np.all(tokens>0) and np.all(chars>0)
    assert list(a["case_names"])==plan["case_order"]
    assert list(a["policies"])==plan["policy_order"]
    z=ll-np.max(ll,axis=-1,keepdims=True)
    lp=z-np.log(np.exp(z).sum(axis=-1,keepdims=True))
    accuracy=np.argmax(ll,axis=-1)==gold[None,None,:]
    char_accuracy=np.argmax(ll/chars[None,None,:,:],axis=-1)==gold[None,None,:]
    ce=np.empty((4,3,128))
    token_nll=np.empty_like(ce)
    margin=np.empty_like(ce)
    for c in range(4):
        for p in range(3):
            for q,g in enumerate(gold):
                ce[c,p,q]=-lp[c,p,q,g]
                token_nll[c,p,q]=-ll[c,p,q,g]/tokens[q,g]
                margin[c,p,q]=ll[c,p,q,g]-max(ll[c,p,q,j] for j in range(4) if j!=g)
    metrics={"raw_accuracy":accuracy.astype(float),"per_char_accuracy":char_accuracy.astype(float),
             "choice_CE":ce,"true_answer_token_NLL":token_nll,"correct_margin":margin}
    errors={}
    check=lambda label,actual,record:errors.update({label:abs(mean_by_subject(actual,topics)-record["point"])})
    for c,name in enumerate(a["case_names"]):
        for p,policy in enumerate(a["policies"]):
            record=summary["cases"][str(name)][str(policy)]
            for metric,values in metrics.items():
                check(f"{name}/{policy}/{metric}",values[c,p],record[metric])
            check(f"{name}/{policy}/first_KL",kl[c,p],record["first_answer_token_KL"])
            choice_kl=np.sum(np.exp(lp[c,0])*(lp[c,0]-lp[c,p]),axis=-1)
            assert np.min(choice_kl)>-2e-13
            check(f"{name}/{policy}/choice_KL",choice_kl,record["choice_score_KL"])
            if p:
                check(f"{name}/{policy}/drop",accuracy[c,0].astype(float)-accuracy[c,p],record["accuracy_drop_from_same_full"])
                check(f"{name}/{policy}/CE_penalty",ce[c,p]-ce[c,0],record["choice_CE_increase_from_same_full"])
    for p,policy in enumerate(a["policies"]):
        pair=summary["native_B_minus_A"][str(policy)]
        interaction=summary["G_x_body_interactions"][str(policy)]
        for metric,v in metrics.items():
            check(f"B-A/{policy}/{metric}",v[3,p]-v[0,p],pair[metric])
            check(f"Gxbody/{policy}/{metric}",v[3,p]-v[2,p]-v[1,p]+v[0,p],interaction[metric])
        if p:
            delta=ce[:,p]-ce[:,0]
            drop=accuracy[:,0].astype(float)-accuracy[:,p]
            check(f"B-A/{policy}/CE_penalty",delta[3]-delta[0],pair["choice_CE_penalty"])
            check(f"B-A/{policy}/drop",drop[3]-drop[0],pair["accuracy_drop"])
            check(f"Gxbody/{policy}/CE_penalty",delta[3]-delta[2]-delta[1]+delta[0],interaction["choice_CE_penalty"])
    supplementary=ROOT/"source_effects.json"
    if supplementary.exists():
        extra=read(supplementary)
        assert extra["raw_sha256"]==manifest["raw"]["sha256"]
        operators={"G_B_minus_G_A_in_A_body":np.array([-1,1,0,0]),
                   "G_B_minus_G_A_in_B_body":np.array([0,0,-1,1]),
                   "body_B_minus_body_A_with_A_gate":np.array([-1,0,1,0]),
                   "body_B_minus_body_A_with_B_gate":np.array([0,-1,0,1]),
                   "average_gate_source":np.array([-1,1,-1,1])/2,
                   "average_body_source":np.array([-1,-1,1,1])/2}
        values={k:v for k,v in metrics.items() if k!="correct_margin"}
        values["first_answer_token_KL"]=kl
        for p,policy in enumerate(a["policies"]):
            for label,w in operators.items():
                record=extra["policies"][str(policy)][label]
                for field,v in values.items():
                    if not (p==0 and field=="first_answer_token_KL"):
                        check(f"source/{policy}/{label}/{field}",sum(w[i]*v[i,p] for i in range(4)),record[field])
                    if p and field!="first_answer_token_KL":
                        check(f"source/{policy}/{label}/{field}/change",sum(w[i]*(v[i,p]-v[i,0]) for i in range(4)),record[field+"_change_from_same_full"])
    assert max(errors.values())<1e-11,errors
    ledger=read(ROOT/"budget.json")
    assert all(x["status"]=="complete" for x in ledger["attempts"])
    result={"status":"passed","CPU_only":True,"audit_source_sha256":sha(__file__),
            "raw_sha256":manifest["raw"]["sha256"],"max_point_error":max(errors.values()),
            "contrasts_checked":len(errors),"errors":errors,
            "selector_budget_and_greedy_rank_verified":True,"source_labels_and_answer_lengths_match_frozen_inputs":True,
            "GPU_seconds":sum(x["gpu_seconds"] for x in ledger["attempts"]),
            "scope":"Independent array calculations by the same researcher; not independent L3 review, new inference, model seeds or whole-MMLU evidence."}
    (ROOT/"raw_verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("status","max_point_error","contrasts_checked","GPU_seconds")},indent=2))


if __name__=="__main__":
    main()
