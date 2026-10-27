"""Independent E155 array audit and remaining preregistered source contrasts."""
import hashlib
import json
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parents[1]/"results/e155"
TASK=OUT.parent/"e153"
SOURCES=("P","A","B")
CONDITIONS=("native","routed_zero","shared_zero","all_moe_zero")
TOPICS=("high_school_biology","high_school_mathematics")


def read(p):
    return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def stats(v,topics):
    rng=np.random.default_rng(155001)
    samples=[]
    points=[]
    detail={}
    for i,label in enumerate(TOPICS):
        values=np.asarray(v,dtype=float)[topics==i]
        draw=values[rng.integers(0,len(values),(1000,len(values)))].mean(1)
        points.append(float(values.mean()))
        samples.append(draw)
        detail[label]={"point":points[-1],"ci95":np.quantile(draw,[.025,.975]).tolist(),"questions":len(values)}
    return {"point":float(np.mean(points)),"question_ci95":np.quantile(np.mean(samples,axis=0),[.025,.975]).tolist(),
            "per_subject":detail,"bootstrap_seed":155001,"question_count":len(v)}


def main():
    plan=read(OUT/"plan.json")
    summary=read(OUT/"summary.json")
    task=read(TASK/"manifest.json")
    assert summary["status"]=="complete"
    assert sha(task["raw"]["path"])==task["raw"]["sha256"]
    with np.load(task["raw"]["path"]) as f:
        original=f["candidate_loglikelihood"].copy()
    arrays=[]
    errors={}
    seconds=0.
    def check(label,values,record,topics):
        s=stats(values,topics)
        errors[label]=abs(s["point"]-record["point"])
        assert np.allclose(s["question_ci95"],record["question_ci95"],atol=2e-12,rtol=0)
    for source in SOURCES:
        m=read(OUT/f"manifest_{source}.json")
        assert m["status"]=="complete" and all(m["controls"].values())
        assert m["source_sha256"]==plan["source_sha256"]==read(OUT/"self_test.json")["source_sha256"]
        assert m["plan_sha256"]==sha(OUT/"plan.json") and sha(m["raw"]["path"])==m["raw"]["sha256"]
        with np.load(m["raw"]["path"]) as f:
            a={k:f[k].copy() for k in f.files}
        ll=a["candidate_loglikelihood"].astype(float)
        gold=a["gold"]
        topics=a["subject"]
        assert ll.shape==(4,128,4) and np.isfinite(ll).all() and np.all(ll<=0)
        assert list(a["conditions"])==list(CONDITIONS) and np.array_equal(np.bincount(topics),[64,64])
        assert np.all(a["first_answer_token_KL"][0]==0) and np.min(a["first_answer_token_KL"])>=-1e-6
        if source!="P":
            assert np.array_equal(ll[0],original[0 if source=="A" else 3,0])
        x=ll-ll.max(-1,keepdims=True)
        lp=x-np.log(np.exp(x).sum(-1,keepdims=True))
        correct=(ll.argmax(-1)==gold).astype(float)
        char_correct=((ll/a["answer_chars"]).argmax(-1)==gold).astype(float)
        ce=np.empty((4,128))
        nll=np.empty_like(ce)
        for c in range(4):
            for q,g in enumerate(gold):
                ce[c,q]=-lp[c,q,g]
                nll[c,q]=-ll[c,q,g]/a["answer_tokens"][q,g]
        values={"raw_accuracy":correct,"per_char_accuracy":char_correct,"choice_CE":ce,"true_answer_token_NLL":nll,
                "first_answer_token_KL":a["first_answer_token_KL"].astype(float)}
        for c,name in enumerate(CONDITIONS):
            row=summary["sources"][source][name]
            for field,v in values.items():
                check(f"{source}/{name}/{field}",v[c],row[field],topics)
            if c:
                check(f"{source}/{name}/drop",correct[0]-correct[c],row["accuracy_drop"],topics)
                for field in ("choice_CE","true_answer_token_NLL"):
                    check(f"{source}/{name}/{field}/increase",values[field][c]-values[field][0],row[field+"_increase"],topics)
        for field,v in values.items():
            if field!="first_answer_token_KL":
                check(f"{source}/RxS/{field}",v[0]-v[1]-v[2]+v[3],summary["sources"][source]["R_x_S_interaction"][field],topics)
        ledger=read(OUT/f"budget_{source}.json")
        assert all(x["status"]=="complete" for x in ledger["attempts"])
        seconds+=sum(x["gpu_seconds"] for x in ledger["attempts"])
        arrays.append((a,values))
    for a,_ in arrays[1:]:
        for key in ("gold","subject","answer_tokens","answer_chars"):
            assert np.array_equal(a[key],arrays[0][0][key])
    topics=arrays[0][0]["subject"]
    extra={"experiment":"E155","status":"complete","source_sha256":sha(__file__),"purpose":"Complete the preregistered KL and answer-NLL source contrasts, with unchanged questions and operators.","source_differences":{}}
    for i,j,label in ((1,0,"A_minus_P"),(2,0,"B_minus_P"),(2,1,"B_minus_A")):
        rows={}
        left,right=arrays[i][1],arrays[j][1]
        for c,name in enumerate(CONDITIONS):
            record=summary["source_differences"][label][name]
            for field in ("raw_accuracy","per_char_accuracy","choice_CE","true_answer_token_NLL"):
                check(f"{label}/{name}/{field}",left[field][c]-right[field][c],record[field],topics)
            row={"first_answer_token_KL":stats(left["first_answer_token_KL"][c]-right["first_answer_token_KL"][c],topics)}
            if c:
                check(f"{label}/{name}/drop",(left["raw_accuracy"][0]-left["raw_accuracy"][c])-(right["raw_accuracy"][0]-right["raw_accuracy"][c]),record["accuracy_drop"],topics)
                check(f"{label}/{name}/CE_increase",(left["choice_CE"][c]-left["choice_CE"][0])-(right["choice_CE"][c]-right["choice_CE"][0]),record["choice_CE_increase"],topics)
                row["true_answer_token_NLL_increase"]=stats((left["true_answer_token_NLL"][c]-left["true_answer_token_NLL"][0])-(right["true_answer_token_NLL"][c]-right["true_answer_token_NLL"][0]),topics)
            rows[name]=row
        extra["source_differences"][label]=rows
    assert max(errors.values())<2e-12
    report={"status":"passed","CPU_only":True,"audit_source_sha256":sha(__file__),"max_point_error":max(errors.values()),
            "contrasts_checked":len(errors),"point_errors":errors,"paired_CIs_recomputed":True,"GPU_seconds":seconds,
            "scope":"Separate raw-array calculation by the same researcher; no independent L3 review, new model runs or training-seed evidence."}
    (OUT/"remaining_preregistered_contrasts.json").write_text(json.dumps(extra,indent=2)+"\n")
    (OUT/"raw_verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","max_point_error","contrasts_checked","GPU_seconds")},indent=2))


if __name__=="__main__":
    main()
