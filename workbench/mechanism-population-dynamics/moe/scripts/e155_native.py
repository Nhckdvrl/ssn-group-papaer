"""E155: native, all-routed-zero and all-shared-zero on fixed RC tasks."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu",type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None,"",str(_early.physical_gpu)):
    raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"]=str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
import json
from contextlib import ExitStack
from pathlib import Path
import numpy as np
import torch
import e150_native as n
import e151_native as v
import e153_harness as h
import e154_native as parent

RESULT=n.WB/"results/e155"
RAW=Path.home()/"mechpop_cache/e155_native_task_branch_necessity"
TASK=n.WB/"results/e153"
SOURCES=("P","A","B")
CONDITIONS=("native","routed_zero","shared_zero","all_moe_zero")
TOPICS=("high_school_biology","high_school_mathematics")


def proof():
    return {**parent.proof(),**{f:n.sha(n.WB/"scripts"/f) for f in ("e153_harness.py","e155_native.py")}}


def question_stats(v,topics):
    rng=np.random.default_rng(155001)
    draws=[]
    points=[]
    details={}
    for i,label in enumerate(TOPICS):
        x=np.asarray(v,dtype=float)[topics==i]
        sample=x[rng.integers(0,len(x),(1000,len(x)))].mean(1)
        points.append(float(x.mean()))
        draws.append(sample)
        details[label]={"point":points[-1],"ci95":np.quantile(sample,[.025,.975]).tolist(),"questions":len(x)}
    return {"point":float(np.mean(points)),"question_ci95":np.quantile(np.mean(draws,axis=0),[.025,.975]).tolist(),
            "per_subject":details,"bootstrap_seed":155001,"question_count":len(v)}


def metrics(scores,gold,tokens,chars):
    q=np.arange(len(gold))
    x=scores-scores.max(-1,keepdims=True)
    lp=x-np.log(np.exp(x).sum(-1,keepdims=True))
    return {"raw_accuracy":(scores.argmax(-1)==gold).astype(float),
            "per_char_accuracy":((scores/chars).argmax(-1)==gold).astype(float),
            "choice_CE":-lp[:,q,gold],"true_answer_token_NLL":-scores[:,q,gold]/tokens[q,gold]}


def self_test():
    old=n.read(TASK/"self_test.json")
    assert old["status"]=="passed" and old["source_sha256"]["e153_harness.py"]==n.sha(h.__file__)
    assert n.read(v.RESULT/"self_test.json")["source_sha256"]["e151_native.py"]==n.sha(v.__file__)
    assert n.read(parent.RESULT/"self_test.json")["source_sha256"]==parent.proof()
    from torch import nn
    cfg_cls,_,_=n.classes(0)
    module=__import__("codex_e150_source_0.modeling_emo",fromlist=["EmoSparseMoeBlock"])
    cfg=cfg_cls(hidden_size=4,intermediate_size=4,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False)
    block=module.EmoSparseMoeBlock(cfg,4,1,None)
    block.gate=v.FixedGate()
    block.experts=nn.ModuleList([v.Constant(x) for x in (2.,4.,8.,10.)])
    fixture=nn.Module()
    fixture.model=nn.Module()
    layer=nn.Module()
    layer.mlp=block
    fixture.model.layers=nn.ModuleList([layer])
    before=n.old.tensor_hash(fixture.state_dict())
    hidden=torch.ones((1,4,4))
    with v.suppress(fixture,"routed"),v.suppress(fixture,"shared"):
        assert torch.equal(fixture.model.layers[0].mlp(hidden)[0],torch.zeros_like(hidden))
    assert n.old.tensor_hash(fixture.state_dict())==before
    gold=np.array([0,1,2,3])
    logits=np.array([[0,-1,-2,-3],[-1,0,-2,-3],[-2,-1,0,-3],[0,-2,-3,-1]],float)[None]
    values=metrics(logits,gold,np.ones((4,4)),np.ones((4,4)))
    assert values["raw_accuracy"].mean()==.75 and values["true_answer_token_NLL"].mean()==.25
    assert question_stats(np.ones(4),np.array([0,0,1,1]))["question_ci95"]==[1.,1.]
    n.write(RESULT/"self_test.json",{"status":"passed","CPU_only":True,"source_sha256":proof(),
            "reused_frozen_task_harness_oracles":True,"reused_A_B_P_R_S_zero_oracles":True,
            "task_metrics_known_answer":True,"stratified_question_stats_known_answer":True,"nested_R_S_zero_known_answer_and_restore":True})
    return {"status":"passed"}


def prepare():
    tests=n.read(RESULT/"self_test.json")
    if tests["source_sha256"]!=proof():
        raise ValueError("Matching preflight source required")
    task=n.read(TASK/"manifest.json")
    data=n.read(TASK/"data_plan.json")
    pp=n.read(parent.RESULT/"preflight.json")
    pa=parent.metadata(complete=True)
    if task["status"]!="complete" or pp["status"]!="complete":
        raise ValueError("Complete previous task and parent native calibration required")
    for record in (task["raw"],data["data"],pp["raw"]):
        if n.sha(record["path"])!=record["sha256"]:
            raise ValueError("Sealed input/reference bytes changed")
    RAW.mkdir(exist_ok=True,parents=True)
    n.old.immutable_json(RESULT/"plan.json",{"experiment":"E155","status":"prepared","source_sha256":proof(),
        "data_plan_sha256":n.sha(TASK/"data_plan.json"),"task_manifest_sha256":n.sha(TASK/"manifest.json"),
        "parent_preflight_sha256":n.sha(parent.RESULT/"preflight.json"),"parent_asset_manifest_sha256":n.sha(parent.RESULT/"asset_manifest.json"),
        "input":data["data"],"native_task_reference":task["raw"],"pad_token_id":data["pad_token_id"],
        "sources":list(SOURCES),"conditions":list(CONDITIONS),"bootstrap_seed":155001,
        "scope":"Same fixed two-subject task; three published lineage positions, no training or seed population."})
    return {"status":"prepared"}


class Budget(n.old.Budget):
    def __init__(self,label):
        self.path,self.experiment,self.phase,self.limit=RESULT/f"budget_{label}.json","e155",f"task_branch_necessity_{label}",3600


def sequences(flat,offsets,indices):
    return [flat[offsets[i]:offsets[i+1]] for i in indices]


def load(label):
    if label!="P":
        return n.load_bf16("AB".index(label))
    parent.metadata(complete=True)
    cfg_cls,cls,root=parent.classes()
    cfg=cfg_cls.from_json_file(root/"config.json")
    model,info=cls.from_pretrained(root,config=cfg,dtype=torch.float32,local_files_only=True,
                                  attn_implementation="sdpa",output_loading_info=True)
    if any(info.get(k) for k in ("missing_keys","unexpected_keys","mismatched_keys","error_msgs")):
        raise ValueError("Parent keys differ")
    model=model.to("cuda:0").eval().requires_grad_(False).bfloat16()
    torch.cuda.empty_cache()
    return model


@torch.no_grad()
def evaluate(label,physical):
    plan=n.read(RESULT/"plan.json")
    if plan["source_sha256"]!=proof() or n.read(RESULT/"self_test.json")["source_sha256"]!=proof():
        raise ValueError("Frozen source differs")
    for path,key in ((TASK/"data_plan.json","data_plan_sha256"),(TASK/"manifest.json","task_manifest_sha256"),
                     (parent.RESULT/"preflight.json","parent_preflight_sha256"),(parent.RESULT/"asset_manifest.json","parent_asset_manifest_sha256")):
        if n.sha(path)!=plan[key]:
            raise ValueError("Sealed dependencies changed")
    for record in (plan["input"],plan["native_task_reference"]):
        if n.sha(record["path"])!=record["sha256"]:
            raise ValueError("Frozen input/native reference differs")
    with np.load(plan["input"]["path"]) as f:
        a={k:f[k].copy() for k in f.files}
    with np.load(plan["native_task_reference"]["path"]) as f:
        previous=f["candidate_loglikelihood"].copy()
    legacy=n.read(n.RESULT/"plan.json")
    with np.load(legacy["path"]) as f:
        cal=f["cal"][:2,:129].copy()
        cv=f["cal_mask"][:2,:128].copy()
    reference_record=n.read(parent.RESULT/"preflight.json")["raw"] if label=="P" else n.read(n.RESULT/"preflight.json")["models"][str("AB".index(label))]["cal_BF16_logits"]
    if n.sha(reference_record["path"])!=reference_record["sha256"]:
        raise ValueError("Native calibration changed")
    target=RAW/f"scores_{label}.npz"
    if target.exists():
        raise ValueError("Refusing to replace source task raw")
    lock=None
    try:
        with Budget(label) as budget:
            lock=n.old.gpu_lock(physical)
            budget.check()
            model=load(label)
            with np.load(reference_record["path"]) as f:
                expected=torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
            ids=torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            attention=torch.cat((torch.ones((2,1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(cv).to("cuda:0")),1)
            if not torch.equal(n.fwd(model,ids[:,:-1],attention[:,:-1]),expected):
                raise ValueError("Native parameter/buffer program differs")
            del expected,ids,attention
            before=n.old.tensor_hash(model.state_dict())
            before_buffers=n.old.tensor_hash(n.buffers(model))
            count=len(a["gold"])
            scores=np.empty((4,count,4),np.float64)
            kl=np.empty((4,count),np.float64)
            for q in range(count):
                budget.check()
                seqs=sequences(a["test_ids"],a["test_offsets"],range(q*4,q*4+4))
                prompt=int(a["prompt_tokens"][q])
                native,counts,ref=h.score_candidates(model,seqs,prompt,plan["pad_token_id"])
                if not np.array_equal(counts,a["answer_tokens"][q]):
                    raise ValueError("Answer mask/count differs")
                if label!="P" and not np.array_equal(native,previous[0 if label=="A" else 3,0,q]):
                    raise ValueError("All-task native replay differs from E153")
                if q==0:
                    with n.restricted.restricted_gates(model,np.ones((4,16,128),bool)):
                        identity,_,first=h.score_candidates(model,seqs,prompt,plan["pad_token_id"])
                    if not np.array_equal(identity,native) or not torch.equal(first,ref):
                        raise ValueError("Full-slot task identity failed")
                    del first
                scores[0,q]=native
                kl[0,q]=0.
                for c,which in ((1,("routed",)),(2,("shared",)),(3,("routed","shared"))):
                    budget.check()
                    with ExitStack() as contexts:
                        for branch in which:
                            contexts.enter_context(v.suppress(model,branch))
                        value,_,current=h.score_candidates(model,seqs,prompt,plan["pad_token_id"])
                    scores[c,q]=value
                    kl[c,q]=float((ref.exp()*(ref-current)).double().sum())
                    del current
                del ref
                if (q+1)%16==0:
                    n.old.emit("E155_questions",source=label,questions=q+1,total=count)
            if n.old.tensor_hash(model.state_dict())!=before or n.old.tensor_hash(n.buffers(model))!=before_buffers:
                raise ValueError("Native source weights/buffers mutated")
            np.savez_compressed(target,candidate_loglikelihood=scores,first_answer_token_KL=kl,gold=a["gold"],subject=a["subject"],
                                answer_tokens=a["answer_tokens"],answer_chars=a["answer_chars"],conditions=np.array(CONDITIONS))
            n.write(RESULT/f"manifest_{label}.json",{"experiment":"E155","status":"complete","source":label,"source_sha256":proof(),
                    "plan_sha256":n.sha(RESULT/"plan.json"),"raw":{"path":str(target),"sha256":n.sha(target),"size_bytes":target.stat().st_size},
                    "controls":{"native_calibration_exact":True,"full_slot_task_identity_exact":True,"candidate_prefix_causal_exact":True,
                                "answer_counts_exact":True,"source_parameters_buffers_unchanged":True,"native_task_replay_exact_where_previous_exists":True},
                    "native_task_reference":"first_P_task_observation_after_E154_cal" if label=="P" else "E153 full candidate scores",
                    "source_parameter_hash":before,"source_buffer_hash":before_buffers,"physical_gpu":physical,
                    "visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),"peak_allocated_bytes":torch.cuda.max_memory_allocated()})
    finally:
        if lock is not None:
            lock.close()
    return {"status":"complete","source":label}


def analyze():
    arrays=[]
    for label in SOURCES:
        m=n.read(RESULT/f"manifest_{label}.json")
        if m["status"]!="complete" or n.sha(m["raw"]["path"])!=m["raw"]["sha256"]:
            raise ValueError("All three sealed sources required")
        with np.load(m["raw"]["path"]) as f:
            arrays.append({k:f[k].copy() for k in f.files})
    for a in arrays[1:]:
        for key in ("gold","subject","answer_tokens","answer_chars","conditions"):
            assert np.array_equal(a[key],arrays[0][key])
    topic=arrays[0]["subject"]
    per_source=[metrics(a["candidate_loglikelihood"].astype(float),a["gold"],a["answer_tokens"],a["answer_chars"]) for a in arrays]
    result={"experiment":"E155","status":"complete","sources":{},"source_differences":{},"source_sha256":proof(),
            "scope":"Question-paired two-subject task. Zeroing is a nonadditive network intervention, not knowledge percentages or training-seed evidence."}
    for i,label in enumerate(SOURCES):
        rows={}
        for c,name in enumerate(CONDITIONS):
            row={field:question_stats(value[c],topic) for field,value in per_source[i].items()}
            row["first_answer_token_KL"]=question_stats(arrays[i]["first_answer_token_KL"][c],topic)
            if c:
                row["accuracy_drop"]=question_stats(per_source[i]["raw_accuracy"][0]-per_source[i]["raw_accuracy"][c],topic)
                for field in ("choice_CE","true_answer_token_NLL"):
                    row[field+"_increase"]=question_stats(per_source[i][field][c]-per_source[i][field][0],topic)
            rows[name]=row
        rows["R_x_S_interaction"]={field:question_stats(value[0]-value[1]-value[2]+value[3],topic) for field,value in per_source[i].items()}
        result["sources"][label]=rows
    for i,j,label in ((1,0,"A_minus_P"),(2,0,"B_minus_P"),(2,1,"B_minus_A")):
        rows={}
        for c,name in enumerate(CONDITIONS):
            row={field:question_stats(per_source[i][field][c]-per_source[j][field][c],topic) for field in per_source[i]}
            if c:
                row["accuracy_drop"]=question_stats((per_source[i]["raw_accuracy"][0]-per_source[i]["raw_accuracy"][c])-
                                                    (per_source[j]["raw_accuracy"][0]-per_source[j]["raw_accuracy"][c]),topic)
                row["choice_CE_increase"]=question_stats((per_source[i]["choice_CE"][c]-per_source[i]["choice_CE"][0])-
                                                        (per_source[j]["choice_CE"][c]-per_source[j]["choice_CE"][0]),topic)
            rows[name]=row
        result["source_differences"][label]=rows
    n.write(RESULT/"summary.json",result)
    return {"status":"complete"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("self-test","prepare","evaluate","analyze"))
    p.add_argument("--source",choices=SOURCES,default="A")
    p.add_argument("--physical-gpu",type=int,default=0)
    args=p.parse_args()
    torch.set_num_threads(4)
    out=self_test() if args.mode=="self-test" else prepare() if args.mode=="prepare" else evaluate(args.source,args.physical_gpu) if args.mode=="evaluate" else analyze()
    print(json.dumps(out,indent=2),flush=True)
