"""E156: P dense/gate receiver, 3x3 routed/shared source functions and task reuse."""
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
from pathlib import Path
import numpy as np
import torch
from torch import nn
import e150_native as n
import e151_native as v
import e153_harness as h
import e154_native as parent
import e156_loading as loading
import e156_analyze as analysis

RESULT=n.WB/"results/e156"
RAW=Path.home()/"mechpop_cache/e156_common_parent_cross"
TASK=n.WB/"results/e153"
PREVIOUS=n.WB/"results/e155"
SOURCES=("P","A","B")
POLICIES=("full","receiverP32")


def proof():
    return {**parent.proof(),**{f:n.sha(n.WB/"scripts"/f) for f in
        ("e153_harness.py","e156_run.py","e156_loading.py","e156_analyze.py")}}


def self_test():
    torch.set_num_threads(1)
    torch.manual_seed(156)
    conversion=loading.self_test()
    statistics=analysis.self_test()
    models=[]
    original_values=[]
    for i,label in enumerate(SOURCES):
        cfg_cls,_,_=loading._classes(label,complete=False)
        name="codex_e154_parent" if label=="P" else f"codex_e150_source_{i-1}"
        module=__import__(name+".modeling_emo",fromlist=["EmoSparseMoeBlock"])
        cfg=cfg_cls(hidden_size=4,intermediate_size=4,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False)
        block=module.EmoSparseMoeBlock(cfg,4,1,None)
        block.gate=v.FixedGate()
        block.experts=nn.ModuleList([v.Constant(x) for x in ((2.,3.,5.)[i],4.,8.,(10.,20.,30.)[i])])
        layer=nn.Module()
        layer.mlp=block
        model=nn.Module()
        model.model=nn.Module()
        model.model.layers=nn.ModuleList([layer])
        models.append(model)
        original_values.append(block(torch.ones((1,6,4)))[0].clone())
    blocks=n.original_blocks(models)
    before=[n.old.tensor_hash(m.state_dict()) for m in models]
    for r in range(3):
        for s in range(3):
            model=n.assemble(models,blocks,(0,0,r,s))
            actual=model.model.layers[0].mlp(torch.ones((1,6,4)))[0]
            expected=(10.,20.,30.)[s]+(4/7)*(2.,3.,5.)[r]
            assert torch.allclose(actual,torch.full_like(actual,expected),atol=2e-6)
            n.restore(models,blocks)
    for i,m in enumerate(models):
        assert m.model.layers[0].mlp is blocks[i][0]
        assert torch.equal(m.model.layers[0].mlp(torch.ones((1,6,4)))[0],original_values[i])
        assert n.old.tensor_hash(m.state_dict())==before[i]
    n.write(RESULT/"self_test.json",{"status":"passed","CPU_only":True,"source_sha256":proof(),
            "CPU_first_conversion":conversion,"statistics":statistics,"all_nine_source_oracles":True,"source_registry_and_values_restored":True})
    return {"status":"passed"}


def calibration(label):
    return n.read(parent.RESULT/"preflight.json")["raw"] if label=="P" else n.read(n.RESULT/"preflight.json")["models"][str("AB".index(label))]["cal_BF16_logits"]


def prepare():
    tests=n.read(RESULT/"self_test.json")
    if tests["status"]!="passed" or tests["source_sha256"]!=proof():
        raise ValueError("Matching complete CPU source tests required")
    data=n.read(TASK/"data_plan.json")
    manifests={}
    references=[]
    for label in SOURCES:
        m=n.read(PREVIOUS/f"manifest_{label}.json")
        ledger=n.read(PREVIOUS/f"budget_{label}.json")
        if m["status"]!="complete" or any(x["status"]!="complete" for x in ledger["attempts"]):
            raise ValueError("Complete source task records required")
        if n.sha(m["raw"]["path"])!=m["raw"]["sha256"]:
            raise ValueError("Old task source differs")
        with np.load(m["raw"]["path"]) as f:
            references.append(f["candidate_loglikelihood"][0].copy())
        record=calibration(label)
        if n.sha(record["path"])!=record["sha256"]:
            raise ValueError("Native calibration proof differs")
        manifests[label]={"manifest_sha256":n.sha(PREVIOUS/f"manifest_{label}.json"),
                          "parameter_hash":m["source_parameter_hash"],"buffer_hash":m["source_buffer_hash"],
                          "calibration":record}
    if n.sha(data["data"]["path"])!=data["data"]["sha256"]:
        raise ValueError("Frozen task inputs differ")
    with np.load(data["data"]["path"]) as f:
        gold=f["gold"].copy()
        subjects=f["subject"].copy()
    scores=np.stack(references)
    common=np.all(scores.argmax(-1)==gold[None,:],axis=0)
    assert common.sum()==44 and [int((common&(subjects==i)).sum()) for i in range(2)]==[36,8]
    RAW.mkdir(exist_ok=True,parents=True)
    path=RAW/"native_references.npz"
    if path.exists():
        with np.load(path) as f:
            assert np.array_equal(f["scores"],scores) and np.array_equal(f["common_success"],common)
    else:
        np.savez_compressed(path,scores=scores,common_success=common)
    legacy=n.read(n.RESULT/"plan.json")
    result={"experiment":"E156","status":"prepared","source_sha256":proof(),"sources":list(SOURCES),"policies":list(POLICIES),
            "task_input":data["data"],"task_data_plan_sha256":n.sha(TASK/"data_plan.json"),"pad_token_id":data["pad_token_id"],
            "native_references":{"path":str(path),"sha256":n.sha(path)},"source_records":manifests,
            "legacy_cal_input":{"path":legacy["path"],"sha256":legacy["sha256"]},"calibration_batch_size":2,
            "common_success":{"questions":44,"subjects":[36,8],"definition":"All E155 native P/A/B raw choices correct; fixed before E156 interventions; secondary only"},
            "scope":"One common mature P dense/gate receiver; all nine R/S source combinations, fixed receiver-native validation selector, no training or model population claim."}
    n.old.immutable_json(RESULT/"plan.json",result)
    return {"status":"prepared"}


class Budget(n.old.Budget):
    def __init__(self):
        self.path,self.experiment,self.phase,self.limit=RESULT/"budget.json","e156","common_P_receiver_R_S_source_cross",9000


def sequences(flat,offsets,indices):
    return [flat[offsets[i]:offsets[i+1]] for i in indices]


def kl(ref,current):
    return float((ref.exp()*(ref-current)).double().sum())


@torch.no_grad()
def evaluate(physical):
    plan=n.read(RESULT/"plan.json")
    if plan["source_sha256"]!=proof() or n.read(RESULT/"self_test.json")["source_sha256"]!=proof():
        raise ValueError("Frozen complete source differs")
    if n.sha(TASK/"data_plan.json")!=plan["task_data_plan_sha256"]:
        raise ValueError("Task recipe differs")
    for record in (plan["task_input"],plan["native_references"],plan["legacy_cal_input"]):
        if n.sha(record["path"])!=record["sha256"]:
            raise ValueError("Frozen source input/reference differs")
    for label,record in plan["source_records"].items():
        if n.sha(PREVIOUS/f"manifest_{label}.json")!=record["manifest_sha256"]:
            raise ValueError("Native source manifest differs")
    target=RAW/"scores.npz"
    if target.exists():
        raise ValueError("Refusing to replace cross source raw")
    with np.load(plan["task_input"]["path"]) as f:
        a={k:f[k].copy() for k in f.files}
    with np.load(plan["native_references"]["path"]) as f:
        expected_native=f["scores"].copy()
        common=f["common_success"].copy()
    with np.load(plan["legacy_cal_input"]["path"]) as f:
        cal=f["cal"][:2,:129].copy()
        cv=f["cal_mask"][:2,:128].copy()
    lock=None
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical)
            models=[]
            before=[]
            before_buffers=[]
            ids=torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            attention=torch.cat((torch.ones((2,1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(cv).to("cuda:0")),1)
            for label in SOURCES:
                budget.check()
                model=loading.load_cpu_bf16(label)
                models.append(model)
                if sum(p.numel() for p in model.parameters())!=13568641024:
                    raise ValueError("Unexpected native source size")
                record=plan["source_records"][label]
                ph=n.old.tensor_hash(model.state_dict())
                bh=n.old.tensor_hash(n.buffers(model))
                if ph!=record["parameter_hash"] or bh!=record["buffer_hash"]:
                    raise ValueError("CPU cast differs from canonical native parameter/buffer bytes")
                before.append(ph)
                before_buffers.append(bh)
                native_cal=record["calibration"]
                if n.sha(native_cal["path"])!=native_cal["sha256"]:
                    raise ValueError("Old calibration raw differs")
                with np.load(native_cal["path"]) as f:
                    expected=torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                actual=n.fwd(model,ids[:,:-1],attention[:,:-1])
                if not torch.equal(actual,expected):
                    raise ValueError("CPU-first source native calibration differs")
                with n.restricted.restricted_gates(model,np.ones((2,16,128),bool)):
                    if not torch.equal(n.fwd(model,ids[:,:-1],attention[:,:-1]),expected):
                        raise ValueError("Source full mask identity differs")
                del expected,actual
                n.old.emit("E156_source_loaded",source=label,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            blocks=n.original_blocks(models)
            with np.load(plan["source_records"]["P"]["calibration"]["path"]) as f:
                expected=torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
            identity=n.assemble(models,blocks,(0,0,0,0))
            if not torch.equal(n.fwd(identity,ids[:,:-1],attention[:,:-1]),expected):
                raise ValueError("P/P real source assembly identity differs")
            n.restore(models,blocks)
            del ids,attention,expected
            masks=np.empty((2,16,128),bool)
            probabilities=np.empty((2,16,127),np.float64)
            for topic in range(2):
                indices=np.flatnonzero(a["cal_subject"]==topic)
                seqs=sequences(a["cal_ids"],a["cal_offsets"],indices)
                def progress(layer,keep,probs):
                    budget.check()
                    n.old.emit("E156_receiver_greedy",subject=topic,layer=layer)
                keep,prob,counts=h.greedy_masks(models[0],seqs,plan["pad_token_id"],32,plan["calibration_batch_size"],progress)
                masks[topic]=keep
                probabilities[topic]=prob
            mask_path=RAW/"receiver_task_masks.npz"
            if mask_path.exists():
                raise ValueError("Refusing to replace receiver selector")
            np.savez_compressed(mask_path,masks=masks,mean_probabilities=probabilities)
            n.write(RESULT/"selectors.json",{"status":"complete","source":"P native","calibration_only":True,"test_labels_used":False,
                    "raw":{"path":str(mask_path),"sha256":n.sha(mask_path)},"source_sha256":proof()})
            count=len(a["gold"])
            values=np.empty((3,3,2,count,4),np.float64)
            native=np.empty((3,2,count,4),np.float64)
            relative=np.empty((3,3,2,count),np.float64)
            pruning=np.empty((3,3,count),np.float64)
            native_relative=np.empty((3,2,count),np.float64)
            native_pruning=np.empty((3,count),np.float64)
            for question in range(count):
                budget.check()
                n.restore(models,blocks)
                seqs=sequences(a["test_ids"],a["test_offsets"],range(question*4,question*4+4))
                prompt=int(a["prompt_tokens"][question])
                topic=int(a["subject"][question])
                keep=np.broadcast_to(masks[topic],(4,16,128)).copy()
                refs=[]
                for source,model in enumerate(models):
                    score,counts,first=h.score_candidates(model,seqs,prompt,plan["pad_token_id"])
                    if not np.array_equal(counts,a["answer_tokens"][question]) or not np.array_equal(score,expected_native[source,question]):
                        raise ValueError("All-question native replay differs from E155")
                    native[source,0,question]=score
                    refs.append(first)
                for source,model in enumerate(models):
                    native_relative[source,0,question]=kl(refs[0],refs[source])
                    with n.restricted.restricted_gates(model,keep):
                        score,_,first=h.score_candidates(model,seqs,prompt,plan["pad_token_id"])
                    native[source,1,question]=score
                    native_relative[source,1,question]=kl(refs[0],first)
                    native_pruning[source,question]=kl(refs[source],first)
                    del first
                for r in range(3):
                    for s in range(3):
                        budget.check()
                        if r==0 and s==0:
                            values[r,s,:,question]=native[0,:,question]
                            relative[r,s,:,question]=native_relative[0,:,question]
                            pruning[r,s,question]=native_pruning[0,question]
                            continue
                        model=n.assemble(models,blocks,(0,0,r,s))
                        score,_,full=h.score_candidates(model,seqs,prompt,plan["pad_token_id"])
                        values[r,s,0,question]=score
                        relative[r,s,0,question]=kl(refs[0],full)
                        with n.restricted.restricted_gates(model,keep):
                            score,_,masked=h.score_candidates(model,seqs,prompt,plan["pad_token_id"])
                        values[r,s,1,question]=score
                        relative[r,s,1,question]=kl(refs[0],masked)
                        pruning[r,s,question]=kl(full,masked)
                        del full,masked
                del refs
                if (question+1)%8==0:
                    n.old.emit("E156_questions",questions=question+1,total=count,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            n.restore(models,blocks)
            if any(n.old.tensor_hash(m.state_dict())!=x for m,x in zip(models,before)):
                raise ValueError("Source parameters mutated")
            if any(n.old.tensor_hash(n.buffers(m))!=x for m,x in zip(models,before_buffers)):
                raise ValueError("Source buffers mutated")
            for array in (values,native,relative,pruning,native_relative,native_pruning):
                if not np.isfinite(array).all():
                    raise ValueError("Nonfinite cross-source metrics")
            np.savez_compressed(target,candidate_loglikelihood=values,native_candidate_loglikelihood=native,
                    first_answer_token_KL_vs_P=relative,pruning_KL=pruning,native_first_answer_token_KL_vs_P=native_relative,
                    native_pruning_KL=native_pruning,gold=a["gold"],subject=a["subject"],answer_tokens=a["answer_tokens"],
                    answer_chars=a["answer_chars"],common_success=common,source_names=np.array(SOURCES),policies=np.array(POLICIES))
            n.write(RESULT/"manifest.json",{"experiment":"E156","status":"complete","source_sha256":proof(),
                    "plan_sha256":n.sha(RESULT/"plan.json"),"selectors_sha256":n.sha(RESULT/"selectors.json"),
                    "raw":{"path":str(target),"sha256":n.sha(target),"size_bytes":target.stat().st_size},
                    "source_parameter_hashes":before,"source_buffer_hashes":before_buffers,
                    "controls":{"CPU_cast_parameter_and_buffer_bytes_canonical":True,"all_native_calibration_exact":True,
                                "all_native_full_mask_exact":True,"P_P_assembly_calibration_exact":True,"all_native_task_scores_exact_E155":True,
                                "receiver_selector_validation_only":True,"all_candidate_prefixes_causal_exact":True,
                                "source_parameters_and_buffers_unchanged":True},
                    "physical_gpu":physical,"visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),
                    "peak_allocated_bytes":torch.cuda.max_memory_allocated(),
                    "scope":"Common P D/G parameters, nine R/S function source cells and a fixed receiver-native task selector. H/routes can change; no training."})
    finally:
        if lock is not None:
            lock.close()
    return {"status":"complete"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("self-test","prepare","evaluate"))
    p.add_argument("--physical-gpu",type=int,default=0)
    args=p.parse_args()
    torch.set_num_threads(4)
    out=self_test() if args.mode=="self-test" else prepare() if args.mode=="prepare" else evaluate(args.physical_gpu)
    print(json.dumps(out,indent=2),flush=True)
