"""Complete the preregistered E153 simple source contrasts; no new inference."""
import hashlib
import json
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parents[1]/"results/e153"
TOPICS=("high_school_biology","high_school_mathematics")
POLICIES=("full","selectorA32","selectorB32")


def sha(p):
    with Path(p).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def stats(v,topic):
    rng=np.random.default_rng(153001)
    points=[]
    draws=[]
    details={}
    for i,label in enumerate(TOPICS):
        values=v[topic==i]
        sampled=values[rng.integers(0,len(values),(1000,len(values)))].mean(1)
        points.append(float(values.mean()))
        draws.append(sampled)
        details[label]={"point":points[-1],"ci95":np.quantile(sampled,[.025,.975]).tolist(),"questions":len(values)}
    return {"point":float(np.mean(points)),"question_ci95":np.quantile(np.mean(draws,axis=0),[.025,.975]).tolist(),
            "per_subject":details,"question_count":len(v),"bootstrap_seed":153001}


def main():
    m=json.loads((OUT/"manifest.json").read_text())
    s=json.loads((OUT/"summary.json").read_text())
    assert m["status"]==s["status"]=="complete" and sha(m["raw"]["path"])==m["raw"]["sha256"]
    with np.load(m["raw"]["path"]) as f:
        ll=f["candidate_loglikelihood"].astype(float)
        first=f["first_answer_token_KL"].astype(float)
        gold=f["gold"].copy()
        topic=f["subject"].copy()
        chars=f["answer_chars"].copy()
        tokens=f["answer_tokens"].copy()
    q=np.arange(len(gold))
    x=ll-ll.max(-1,keepdims=True)
    lp=x-np.log(np.exp(x).sum(-1,keepdims=True))
    metrics={"raw_accuracy":(ll.argmax(-1)==gold[None,None,:]).astype(float),
             "per_char_accuracy":((ll/chars[None,None,:,:]).argmax(-1)==gold[None,None,:]).astype(float),
             "choice_CE":-lp[:,:,q,gold],"true_answer_token_NLL":-ll[:,:,q,gold]/tokens[q,gold][None,None,:],
             "first_answer_token_KL":first}
    operators={"G_B_minus_G_A_in_A_body":np.array([-1,1,0,0]),
               "G_B_minus_G_A_in_B_body":np.array([0,0,-1,1]),
               "body_B_minus_body_A_with_A_gate":np.array([-1,0,1,0]),
               "body_B_minus_body_A_with_B_gate":np.array([0,-1,0,1]),
               "average_gate_source":np.array([-1,1,-1,1])/2,
               "average_body_source":np.array([-1,-1,1,1])/2}
    result={"experiment":"E153","status":"complete","raw_sha256":m["raw"]["sha256"],"source_sha256":sha(__file__),
            "purpose":"Simple paired source effects specified by the original G x body card; supplements the frozen main summary without changing scores, samples or metrics.",
            "policies":{},"scope":"Four fixed source cases, two fixed selectors, two subjects. Body includes D/R/S; its effect can act through H and actual routing. No causal responsibility percentages."}
    for p,label in enumerate(POLICIES):
        rows={}
        for name,w in operators.items():
            record={metric:stats(np.einsum("c,cq->q",w,v[:,p]),topic) for metric,v in metrics.items()
                    if not (p==0 and metric=="first_answer_token_KL")}
            if p:
                for metric in ("raw_accuracy","per_char_accuracy","choice_CE","true_answer_token_NLL"):
                    record[metric+"_change_from_same_full"]=stats(np.einsum("c,cq->q",w,metrics[metric][:,p]-metrics[metric][:,0]),topic)
            rows[name]=record
        result["policies"][label]=rows
    for p,label in enumerate(POLICIES):
        expected=s["native_B_minus_A"][label]["raw_accuracy"]
        actual=stats(metrics["raw_accuracy"][3,p]-metrics["raw_accuracy"][0,p],topic)
        assert actual["point"]==expected["point"] and actual["question_ci95"]==expected["question_ci95"]
    (OUT/"source_effects.json").write_text(json.dumps(result,indent=2)+"\n")
    for policy in POLICIES[1:]:
        for effect in ("G_B_minus_G_A_in_A_body","body_B_minus_body_A_with_A_gate"):
            row=result["policies"][policy][effect]
            print(policy,effect,{field:row[field] for field in ("raw_accuracy_change_from_same_full","choice_CE_change_from_same_full")})


if __name__=="__main__":
    main()
