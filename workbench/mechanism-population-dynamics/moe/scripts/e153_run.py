"""E153 task-level RC behavior and G x non-router source transfer."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False);_p.add_argument("--physical-gpu",type=int,default=1)
_early,_=_p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None,"",str(_early.physical_gpu)):raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"]=str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
import json
from pathlib import Path
import numpy as np
import torch
import e150_native as n
import e153_data as d
import e153_harness as h
from transformers import AutoTokenizer

RESULT,RAW=d.RESULT,d.RAW
CASES=((0,0,0,0),(0,1,0,0),(1,0,1,1),(1,1,1,1))
CASE_NAMES=("AAAA","ABAA","BABB","BBBB")
POLICIES=("full","selectorA32","selectorB32")


def proof():
    return {**n.proof(),**{f:n.sha(n.WB/"scripts"/f) for f in ("e153_run.py","e153_harness.py","e153_data.py")}}


def question_stats(values,subjects,seed=153001):
    values=np.asarray(values,dtype=float);subjects=np.asarray(subjects)
    rng=np.random.default_rng(seed);point=[];draw=[];per_topic={}
    for subject in np.unique(subjects):
        v=values[subjects==subject]
        samples=v[rng.integers(0,len(v),size=(1000,len(v)))].mean(1)
        point.append(float(v.mean()));draw.append(samples)
        per_topic[d.SUBJECTS[int(subject)]]={"point":float(v.mean()),"ci95":np.quantile(samples,[.025,.975]).tolist(),"questions":len(v)}
    samples=np.stack(draw).mean(0)
    return {"point":float(np.mean(point)),"question_ci95":np.quantile(samples,[.025,.975]).tolist(),
            "per_subject":per_topic,"question_count":len(values),"bootstrap_seed":seed,"unit":"Question pairs within fixed subjects; not model seeds or subject-population CI"}


def self_test():
    result=h.self_test()
    row={"question":"probe","choices":["one","two","three","four"],"answer":1}
    text=d.context("test_subject",[row]*5,row)
    assert text.count("Question: probe")==6 and text.endswith("Answer:") and text.count("Answer: two")==5
    s=question_stats([0,1,1,1],[0,0,1,1]);assert s["point"]==.75
    assert question_stats([1,1,1,1],[0,0,1,1])["question_ci95"]==[1.,1.]
    result.update(source_sha256=proof(),cloze_dev5_format_known_answer=True,stratified_question_stats_known_answer=True)
    n.write(RESULT/"self_test.json",result)
    return {"status":"passed"}


def prepare():
    tests=n.read(RESULT/"self_test.json");plan=n.read(RESULT/"data_plan.json")
    if tests["source_sha256"]!=proof() or plan["data_source_sha256"]!=n.sha(d.__file__):raise ValueError("Source tests/data recipe differ")
    if n.sha(plan["data"]["path"])!=plan["data"]["sha256"]:raise ValueError("Question token artifact changed")
    metadata=n.assets();root=Path(metadata["models"][n.NAMES[0]]["path"])
    tokenizer=AutoTokenizer.from_pretrained(root,local_files_only=True,trust_remote_code=False)
    controls=[]
    for subject_index,subject in enumerate(d.SUBJECTS):
        info=next((d.CACHE/subject).glob("*/*/dataset_info.json")).parent
        demos=d.load_arrow(info/"mmlu-dev.arrow");row=d.load_arrow(info/"mmlu-validation.arrow")[0]
        prompt=d.context(subject,demos,row);p=tokenizer.encode(prompt,add_special_tokens=False)
        sequences=[tokenizer.encode(prompt+" "+choice,add_special_tokens=False) for choice in row["choices"]]
        if any(seq[:len(p)]!=p for seq in sequences):raise ValueError("Control token boundary differs")
        controls.append({"subject":subject_index,"prompt_tokens":len(p),"sequences":sequences,"gold":int(row["answer"])})
    control_path=RAW/"cal_controls.json"
    if control_path.exists() and n.read(control_path)!=controls:raise ValueError("Refusing to replace control inputs")
    if not control_path.exists():n.write(control_path,controls)
    result={"experiment":"E153","status":"prepared","source_sha256":proof(),"data_plan_sha256":n.sha(RESULT/"data_plan.json"),
            "official_interface_review_sha256":n.sha(RESULT/"official_interface_review.json"),
            "controls":{"path":str(control_path),"sha256":n.sha(control_path)},"case_order":list(CASE_NAMES),"policy_order":list(POLICIES),
            "cal_batch_size":2,"test_batch_unit":"Four full answer candidates for one question","scope":"Task validation of a fixed public pair; no training or literal full-table reproduction"}
    n.old.immutable_json(RESULT/"plan.json",result)
    return {"status":"prepared"}


class Budget(n.old.Budget):
    def __init__(self):self.path,self.experiment,self.phase,self.limit=RESULT/"budget.json","e153","mmlu_cal_and_source_grid",7200


def sequences(flat,offsets,indices):
    return [flat[offsets[i]:offsets[i+1]] for i in indices]


@torch.no_grad()
def evaluate(physical):
    tests=n.read(RESULT/"self_test.json");plan=n.read(RESULT/"plan.json");data=n.read(RESULT/"data_plan.json")
    if tests["source_sha256"]!=proof() or plan["source_sha256"]!=proof():raise ValueError("Frozen source differs")
    if n.sha(RESULT/"data_plan.json")!=plan["data_plan_sha256"] or n.sha(data["data"]["path"])!=data["data"]["sha256"]:raise ValueError("Frozen data differs")
    if n.sha(plan["controls"]["path"])!=plan["controls"]["sha256"]:raise ValueError("Cal controls changed")
    n.ready()
    with np.load(data["data"]["path"]) as f:arrays={k:f[k].copy() for k in f.files}
    with np.load(n.read(n.RESULT/"plan.json")["path"]) as f:legacy_cal=f["cal"][:2,:129].copy();legacy_valid=f["cal_mask"][:2,:128].copy()
    pre=n.read(n.RESULT/"preflight.json");controls=n.read(plan["controls"]["path"]);pad=data["pad_token_id"]
    lock=None
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical);models=[]
            for source in range(2):
                budget.check();model=n.load_bf16(source);models.append(model)
                raw=pre["models"][str(source)]["cal_BF16_logits"]
                if n.sha(raw["path"])!=raw["sha256"]:raise ValueError("Old native control changed")
                with np.load(raw["path"]) as f:expected=torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                ids=torch.from_numpy(legacy_cal.astype(np.int64)).to("cuda:0")
                am=torch.cat((torch.ones((2,1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(legacy_valid).to("cuda:0")),1)
                if not torch.equal(n.fwd(model,ids[:,:-1],am[:,:-1]),expected):raise ValueError("Native code/weight calibration replay differs")
                del ids,am,expected
                for control in controls:
                    seqs=[np.asarray(v,np.uint32) for v in control["sequences"]]
                    reference,counts,first=h.score_candidates(model,seqs,control["prompt_tokens"],pad)
                    full_keep=np.ones((4,16,128),bool)
                    with n.restricted.restricted_gates(model,full_keep):again,_,next_first=h.score_candidates(model,seqs,control["prompt_tokens"],pad)
                    if not np.array_equal(reference,again) or not torch.equal(first,next_first):raise ValueError("Task all-slot mask differs")
                    order=[2,0,3,1]
                    permuted,_,_=h.score_candidates(model,[seqs[i] for i in order],control["prompt_tokens"],pad)
                    if not np.array_equal(permuted,reference[order]):raise ValueError("Task candidate permutation changes scores")
                    del first,next_first
            blocks=n.original_blocks(models)
            before=[n.old.tensor_hash(m.state_dict()) for m in models];before_buffers=[n.old.tensor_hash(n.buffers(m)) for m in models]
            keeps=np.empty((2,2,16,128),bool);probabilities=np.empty((2,2,16,127),np.float64)
            for source,model in enumerate(models):
                for subject in range(2):
                    indices=np.flatnonzero(arrays["cal_subject"]==subject)
                    seqs=sequences(arrays["cal_ids"],arrays["cal_offsets"],indices)
                    budget.check()
                    def progress(layer,keep,probs):
                        budget.check();n.old.emit("E153_greedy_layer",source=source,subject=subject,layer=layer)
                    mask,p,counts=h.greedy_masks(model,seqs,pad,32,plan["cal_batch_size"],progress)
                    keeps[source,subject]=mask;probabilities[source,subject]=p
            mask_path=RAW/"task_masks.npz"
            if mask_path.exists():raise ValueError("Refusing to replace new task masks")
            np.savez_compressed(mask_path,masks=keeps,mean_probabilities=probabilities)
            n.write(RESULT/"selectors.json",{"status":"complete","source_sha256":proof(),"cal_only":True,"test_labels_used":False,
                "mask":{"path":str(mask_path),"sha256":n.sha(mask_path)},"selector":"Sequential per-layer mean FP32 routed softmax on complete validation+dev5 prompts"})
            count=len(arrays["gold"]);scores=np.empty((4,3,count,4),np.float64);first_kl=np.empty((4,3,count),np.float64)
            for question in range(count):
                budget.check();n.restore(models,blocks)
                seqs=sequences(arrays["test_ids"],arrays["test_offsets"],range(question*4,question*4+4))
                prompt=int(arrays["prompt_tokens"][question]);subject=int(arrays["subject"][question])
                for case_index,case in enumerate(CASES):
                    model=n.assemble(models,blocks,case)
                    score,answer_counts,reference=h.score_candidates(model,seqs,prompt,pad)
                    if not np.array_equal(answer_counts,arrays["answer_tokens"][question]):raise ValueError("Scored answer-token counts differ")
                    scores[case_index,0,question]=score;first_kl[case_index,0,question]=0.
                    for selector in range(2):
                        budget.check();mask=np.broadcast_to(keeps[selector,subject],(4,16,128)).copy()
                        with n.restricted.restricted_gates(model,mask):value,_,current=h.score_candidates(model,seqs,prompt,pad)
                        scores[case_index,selector+1,question]=value
                        first_kl[case_index,selector+1,question]=float((reference.exp()*(reference-current)).double().sum())
                        del current
                    del reference
                if (question+1)%8==0:n.old.emit("E153_questions",questions=question+1,total=count,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            n.restore(models,blocks)
            if any(n.old.tensor_hash(m.state_dict())!=hsh for m,hsh in zip(models,before)):raise ValueError("Source parameters mutated")
            if any(n.old.tensor_hash(n.buffers(m))!=hsh for m,hsh in zip(models,before_buffers)):raise ValueError("Source buffers mutated")
            path=RAW/"scores.npz"
            if path.exists():raise ValueError("Refusing to replace question scores")
            np.savez_compressed(path,candidate_loglikelihood=scores,first_answer_token_KL=first_kl,gold=arrays["gold"],subject=arrays["subject"],
                answer_tokens=arrays["answer_tokens"],answer_chars=arrays["answer_chars"],case_names=np.array(CASE_NAMES),policies=np.array(POLICIES))
            result={"experiment":"E153","status":"complete","source_sha256":proof(),"plan_sha256":n.sha(RESULT/"plan.json"),
                "raw":{"path":str(path),"sha256":n.sha(path),"size_bytes":path.stat().st_size},
                "selectors_sha256":n.sha(RESULT/"selectors.json"),"source_parameter_hashes":before,"source_buffer_hashes":before_buffers,
                "controls":{"native_E150_calibration_exact":True,"full_slot_task_scores_exact":True,"candidate_prefix_causal_exact":True,
                    "candidate_permutation_exact":True,"answer_token_masks_exact":True,"source_parameters_buffers_unchanged":True},
                "physical_gpu":physical,"visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),"peak_allocated_bytes":torch.cuda.max_memory_allocated(),
                "scope":"Two fixed subjects,64 test questions each, RC teacher forcing, nativeA/B calibration selectors and fixed Gxbody source grid; no training or full-MMLU reproduction."}
            n.write(RESULT/"manifest.json",result)
    finally:
        if lock is not None:lock.close()
    return {"status":"complete"}


def logsoftmax(a):
    maximum=a.max(-1,keepdims=True)
    return a-maximum-np.log(np.exp(a-maximum).sum(-1,keepdims=True))


def analyze():
    m=n.read(RESULT/"manifest.json")
    if m["status"]!="complete" or m["source_sha256"]!=proof() or n.sha(m["raw"]["path"])!=m["raw"]["sha256"]:raise ValueError("Sealed task results required")
    with np.load(m["raw"]["path"]) as f:
        scores=f["candidate_loglikelihood"].astype(float);gold=f["gold"];subjects=f["subject"]
        tokens=f["answer_tokens"];chars=f["answer_chars"];next_kl=f["first_answer_token_KL"].astype(float)
    q=np.arange(len(gold));choice_logp=logsoftmax(scores)
    metrics={}
    metrics["raw_accuracy"]=(scores.argmax(-1)==gold[None,None,:]).astype(float)
    metrics["per_char_accuracy"]=((scores/chars[None,None,:,:]).argmax(-1)==gold[None,None,:]).astype(float)
    metrics["choice_CE"]=-choice_logp[:,:,q,gold]
    metrics["true_answer_token_NLL"]=-scores[:,:,q,gold]/tokens[q,gold][None,None,:]
    wrong=scores.copy()
    for i,g in enumerate(gold):wrong[:,:,i,g]=-np.inf
    metrics["correct_margin"]=scores[:,:,q,gold]-wrong.max(-1)
    stats=lambda x:question_stats(x,subjects)
    result={"experiment":"E153","status":"complete","cases":{},"native_B_minus_A":{},"G_x_body_interactions":{},
        "scope":"Question-paired uncertainty on two fixed subjects; RC candidate scores, not independent model seeds or all MMLU/semantic-unit evidence."}
    for c,name in enumerate(CASE_NAMES):
        row={}
        for p,policy in enumerate(POLICIES):
            record={metric:stats(value[c,p]) for metric,value in metrics.items()}
            record["first_answer_token_KL"]=stats(next_kl[c,p])
            record["choice_score_KL"]=stats((np.exp(choice_logp[c,0])*(choice_logp[c,0]-choice_logp[c,p])).sum(-1))
            if p:
                record["accuracy_drop_from_same_full"]=stats(metrics["raw_accuracy"][c,0]-metrics["raw_accuracy"][c,p])
                record["choice_CE_increase_from_same_full"]=stats(metrics["choice_CE"][c,p]-metrics["choice_CE"][c,0])
            row[policy]=record
        result["cases"][name]=row
    for p,policy in enumerate(POLICIES):
        result["native_B_minus_A"][policy]={metric:stats(value[3,p]-value[0,p]) for metric,value in metrics.items()}
        result["G_x_body_interactions"][policy]={metric:stats(value[3,p]-value[2,p]-value[1,p]+value[0,p]) for metric,value in metrics.items()}
        if p:
            delta=metrics["choice_CE"][:,p]-metrics["choice_CE"][:,0]
            drops=metrics["raw_accuracy"][:,0]-metrics["raw_accuracy"][:,p]
            result["native_B_minus_A"][policy]["choice_CE_penalty"]=stats(delta[3]-delta[0])
            result["native_B_minus_A"][policy]["accuracy_drop"]=stats(drops[3]-drops[0])
            result["G_x_body_interactions"][policy]["choice_CE_penalty"]=stats(delta[3]-delta[2]-delta[1]+delta[0])
    n.write(RESULT/"summary.json",result)
    return {"status":"complete","native_B_minus_A":result["native_B_minus_A"]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=("self-test","prepare","evaluate","analyze"));p.add_argument("--physical-gpu",type=int,default=1)
    args=p.parse_args();torch.set_num_threads(4)
    out=self_test() if args.mode=="self-test" else prepare() if args.mode=="prepare" else evaluate(args.physical_gpu) if args.mode=="evaluate" else analyze()
    print(json.dumps(out,indent=2),flush=True)
