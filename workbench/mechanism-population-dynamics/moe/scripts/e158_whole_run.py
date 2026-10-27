"""E158 v4: whole terminal paths, reusing verified native component traces."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False);_p.add_argument("--physical-gpu",type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None,"",str(_early.physical_gpu)):raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"]=str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
import json,time
from pathlib import Path
import numpy as np
import torch
import e158_full_run as previous
import e158_whole_engine as engine
import e158_whole_analyze as analysis

n,loading=previous.n,previous.loading
PARENT=n.WB/"results/e158";RESULT=PARENT/"whole_path"
RAW=Path.home()/"mechpop_cache/e158_factual_role_interchange/whole_path"
SOURCES=("P","A","B");SCENARIOS=("entity","attribute","paraphrase");PATHS=("R","S","RS","A")


def proof():
    return {**previous.proof(),**{s:n.sha(n.WB/"scripts"/s) for s in ("e158_whole_run.py","e158_whole_engine.py","e158_whole_analyze.py")}}


def record(path):
    path=Path(path);return {"path":str(path),"sha256":n.sha(path),"size_bytes":path.stat().st_size}


def self_test():
    tests={"whole_path_engine":engine.self_test(),"statistics":analysis.self_test()}
    n.write(RESULT/"self_test.json",{"status":"passed","CPU_only":True,"source_sha256":proof(),"tests":tests,"software":previous.software()})
    return {"status":"passed","CPU_only":True}


def prepare():
    test=n.read(RESULT/"self_test.json")
    if test["status"]!="passed" or test["source_sha256"]!=proof():raise ValueError("Matching complete CPU tests required")
    original=n.read(previous.RESULT/"plan.json");failure=n.read(previous.RESULT/"failed_full_preflight.json")
    ledger=n.read(PARENT/"budget.json");dp=n.read(PARENT/"data_plan.json")
    if len(ledger["attempts"])!=2 or any(x["status"]!="failed" for x in ledger["attempts"]):raise ValueError("Exactly two preserved preflight failures required")
    if failure["attempt"]!=ledger["attempts"][1] or original["source_sha256"]!=previous.proof():raise ValueError("Preserved full-native source differs")
    if failure["readout_floor"]["full_head_to_last_only_head_KL_max"]>.005 or any(v/96>.05 for v in failure["readout_floor"]["argmax_changes"]):raise ValueError("Native head-readout floor failed")
    baseline=record(previous.RAW/"baseline.npz");component=record(previous.RAW/"component_cache.npz")
    if baseline["sha256"]!=failure["baseline"]["sha256"] or component["sha256"]!=failure["components"]["sha256"]:raise ValueError("Preserved source trace bytes differ")
    result={"experiment":"E158","protocol_revision":4,"status":"prepared","source_sha256":proof(),"software":previous.software(),
      "data_plan_sha256":n.sha(PARENT/"data_plan.json"),"data":dp["assets"]["data.npz"],"input_assets":dp["assets"],
      "baseline_reference":baseline,"component_reference":component,"prior_full_preflight":record(previous.RESULT/"failed_full_preflight.json"),
      "prior_failed_budget_attempts":ledger["attempts"],"source_records":original["source_records"],"legacy_cal_input":original["legacy_cal_input"],
      "source_names":list(SOURCES),"scenario_names":list(SCENARIOS),"component_names":list(PATHS),
      "execution_mode":"whole_terminal_path_fixed_native_prefix_no_KV_cache",
      "floor_kind":"inherited actual full-head vs native last-only readout, no KV cache; legacy cache_* compatibility field names",
      "source_trace_protocol_commit":"b522db89","queries":96,"patch_rows":1728,"matched_removal_rows":576,"scientific_rows":2304,
      "positive_residual_rows":432,"all_query_identity_paths":["RS","A"],"fixed_query_extra_identity_paths":["R","S"],
      "baseline_gate":{"joint_native_top10_minimum_per_relation":8},"bootstrap":{"unit":"paired target-country clusters","seed":158001,"resamples":1000},
      "limit_gpu_seconds":14400,"scope":"Complete 16-layer terminal R/S/RS streams plus attention comparator; fixed earlier native decoder positions; current nonreplaced components endogenous; no layer localization or new training."}
    n.old.immutable_json(RESULT/"plan.json",result)
    return {"status":"prepared","scientific_rows":2304,"prior_gpu_seconds":sum(x["gpu_seconds"] for x in ledger["attempts"])}


class Budget(n.old.Budget):
    def __init__(self):self.path,self.experiment,self.phase,self.limit=PARENT/"budget.json","e158","factual_whole_path_interchange",14400


@torch.no_grad()
def evaluate(physical):
    plan=n.read(RESULT/"plan.json")
    if plan["source_sha256"]!=proof() or n.read(RESULT/"self_test.json")["source_sha256"]!=proof() or plan["software"]!=previous.software():raise ValueError("Frozen complete code/software differs")
    if n.read(PARENT/"budget.json")["attempts"]!=plan["prior_failed_budget_attempts"]:raise ValueError("Prior attempt record differs")
    for asset in list(plan["input_assets"].values())+[plan[k] for k in ("baseline_reference","component_reference","prior_full_preflight","legacy_cal_input")]:
        if n.sha(asset["path"])!=asset["sha256"]:raise ValueError("Preserved source/input differs")
    if n.sha(PARENT/"data_plan.json")!=plan["data_plan_sha256"]:raise ValueError("Data recipe differs")
    if (RESULT/"manifest.json").exists() or (RAW/"scores.npz").exists():raise ValueError("Refusing to overwrite completed result")
    RAW.mkdir(parents=True,exist_ok=True)
    def arrays(path):
        with np.load(path,allow_pickle=False) as f:return {k:f[k].copy() for k in f.files}
    a=arrays(plan["data"]["path"]);baseline=arrays(plan["baseline_reference"]["path"]);components=arrays(plan["component_reference"]["path"])
    analysis.base.validate_data(a)
    hits=(baseline["native_top_tokens"]==a["gold_token"][None,:,None]).any(-1)
    joint=hits[:,a["target_query_index"]].all(0).sum(-1);patch=bool(np.all(joint>=8))
    raw={**baseline,"component_names":np.array(PATHS)}
    lock=None
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical)
            selected=torch.from_numpy(a["token_union"].astype(np.int64)).to("cuda:0")
            with np.load(plan["legacy_cal_input"]["path"],allow_pickle=False) as f:cal,cv=f["cal"][:2,:129].copy(),f["cal_mask"][:2,:128].copy()
            ids=torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            attention=torch.cat((torch.ones((2,1),device="cuda:0",dtype=torch.bool),torch.from_numpy(cv).to("cuda:0")),1)
            models,before,buffers=[],[],[]
            for label in SOURCES:
                budget.check();model=loading.load_cpu_bf16(label);models.append(model)
                if sum(p.numel() for p in model.parameters())!=13568641024 or len(model.model.layers)!=16:raise ValueError("Unexpected mature architecture")
                source=plan["source_records"][label];ph,bh=n.old.tensor_hash(model.state_dict()),n.old.tensor_hash(n.buffers(model))
                if ph!=source["parameter_hash"] or bh!=source["buffer_hash"]:raise ValueError("Canonical parameter/buffer bytes differ")
                before.append(ph);buffers.append(bh);c=source["calibration"]
                if n.sha(c["path"])!=c["sha256"]:raise ValueError("Canonical native cal changed")
                with np.load(c["path"],allow_pickle=False) as f:expected=torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                if not torch.equal(n.fwd(model,ids[:,:-1],attention[:,:-1]),expected):raise ValueError("Canonical calibration differs")
                del expected
                n.old.emit("E158_whole_source_loaded",source=label,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            del ids,attention
            query_sets=[];identity_count=0
            for m,(label,model) in enumerate(zip(SOURCES,models)):
                group=[]
                for q in range(96):
                    budget.check();tokens=a["ids"][a["offsets"][q]:a["offsets"][q+1]]
                    reference={k:components[k][m,q] for k in ("hidden","routed","shared","final_residual")}
                    query=engine.capture(model,tokens,reference);group.append(query)
                    if not np.array_equal(query.lp[selected].cpu().numpy(),baseline["native_lp_selected"][m,q]) or not np.array_equal(previous.top10(query.lp),baseline["native_top_tokens"][m,q]):raise ValueError("Native selected LP/top10 replay differs from v3")
                    paths=("R","S","RS","A") if q in (0,48) else ("RS","A")
                    for path in paths:
                        if not torch.equal(engine.interchange(model,query,query,path),query.lp):raise ValueError("Whole-path identity differs")
                        identity_count+=1
                    if (q+1)%24==0:n.old.emit("E158_whole_native_queries",source=label,queries=q+1,total=96,identity_cases=identity_count)
                query_sets.append(group)
            attn=torch.stack([torch.stack([torch.stack(q.attention) for q in group]) for group in query_sets]).squeeze(3).squeeze(3).contiguous().view(torch.uint16).cpu().numpy()
            previous.immutable_npz(RAW/"native_attention.npz",{"attention":attn,"encoding":np.array("bfloat16_uint16_bits")})
            canonical=a["target_query_index"].reshape(-1);bq=int(max(canonical,key=lambda q:(int(a["offsets"][q+1]-a["offsets"][q]),-int(q))))
            t=time.monotonic()
            for _ in range(32):
                value=engine.interchange(models[0],query_sets[0][bq],query_sets[0][bq],"RS")
                if not torch.equal(value,query_sets[0][bq].lp):raise ValueError("Timing identity differs")
            sec=(time.monotonic()-t)/32;remaining=budget.limit-budget.prior-(time.monotonic()-budget.start)
            n.write(RESULT/"runtime_feasibility.json",{"identity_probes":32,"longest_canonical_query":bq,"seconds_per_forward":sec,
                    "remaining_gpu_seconds":remaining,"conservative_grid_seconds":sec*(2304+432)*1.5,"rule":"1.5x scientific plus positive-control rows must fit remaining minus300s"})
            if patch and sec*(2304+432)*1.5>remaining-300:raise TimeoutError("Whole-path grid cannot fit preserved total cap")
            if patch:
                raw.update(positive_lp_selected=np.empty((3,3,2,24,38),np.float32),positive_top_tokens=np.empty((3,3,2,24,10),np.int64))
                for m,model in enumerate(models):
                    for s in range(3):
                        budget.check()
                        for r in range(2):
                            for c in range(24):
                                target=query_sets[m][int(a["target_query_index"][r,c])];source=query_sets[m][int(a["source_query_index"][s,r,c])]
                                value=engine.interchange(model,target,source,"residual")
                                if not torch.equal(value,source.lp):raise ValueError("Source residual positive differs")
                                raw["positive_lp_selected"][m,s,r,c]=value[selected].cpu().numpy();raw["positive_top_tokens"][m,s,r,c]=previous.top10(value)
                raw.update(patched_lp_selected=np.empty((3,3,4,2,24,38),np.float32),patched_top_tokens=np.empty((3,3,4,2,24,10),np.int64),patched_KL_vs_native=np.empty((3,3,4,2,24),np.float64),
                           matched_removal_lp_selected=np.empty((3,4,2,24,38),np.float32),matched_removal_top_tokens=np.empty((3,4,2,24,10),np.int64),matched_removal_KL_vs_native=np.empty((3,4,2,24),np.float64))
                completed,removed=0,0
                for m,(label,model) in enumerate(zip(SOURCES,models)):
                    for s in range(3):
                        for r in range(2):
                            for c in range(24):
                                budget.check();target=query_sets[m][int(a["target_query_index"][r,c])];source=query_sets[m][int(a["source_query_index"][s,r,c])]
                                for p,path in enumerate(PATHS):
                                    if s==0:
                                        value=engine.interchange(model,target,target,"zero_"+path);key=(m,p,r,c)
                                        raw["matched_removal_lp_selected"][key]=value[selected].cpu().numpy();raw["matched_removal_top_tokens"][key]=previous.top10(value)
                                        raw["matched_removal_KL_vs_native"][key]=previous.prev.kl(target.lp,value);removed+=1
                                    value=engine.interchange(model,target,source,path);key=(m,s,p,r,c)
                                    raw["patched_lp_selected"][key]=value[selected].cpu().numpy();raw["patched_top_tokens"][key]=previous.top10(value)
                                    raw["patched_KL_vs_native"][key]=previous.prev.kl(target.lp,value);completed+=1
                                if (c+1)%8==0:n.old.emit("E158_whole_rows",source=label,scenario=SCENARIOS[s],relation=r,countries=c+1,patch_rows=completed,removal_rows=removed)
            for model,ph,bh in zip(models,before,buffers):
                if n.old.tensor_hash(model.state_dict())!=ph or n.old.tensor_hash(n.buffers(model))!=bh:raise ValueError("Source parameters/buffers mutated")
                if any("forward" in d.mlp.__dict__ or d.mlp._forward_hooks or d.mlp._forward_pre_hooks or d.self_attn._forward_hooks or d._forward_hooks for d in model.model.layers):raise ValueError("Native forwards/hooks not restored")
            analysis.validate_raw(raw,patch);path=RAW/"scores.npz";previous.immutable_npz(path,raw)
            n.write(RESULT/"manifest.json",{"experiment":"E158","status":"complete","patch_data_obtained":patch,"plan_sha256":n.sha(RESULT/"plan.json"),"source_sha256":proof(),
                    "execution_mode":plan["execution_mode"],"floor_kind":plan["floor_kind"],"raw":record(path),"attention_components":record(RAW/"native_attention.npz"),
                    "source_parameter_hashes":before,"source_buffer_hashes":buffers,"joint_native_top10":joint.tolist(),"same_query_identity_cases":identity_count,
                    "patch_rows":1728 if patch else 0,"matched_removal_rows":576 if patch else 0,"positive_residual_rows":432 if patch else 0,
                    "controls":{"canonical_parameters_buffers_and_cal_exact":True,"all_native_H_component_sum_final_residual_selected_LP_top10_replay_exact":True,
                                "all_query_RS_attention_full_distribution_identities_exact":True,"current_other_component_endogenous":True,"source_parameters_buffers_and_hooks_restored":True},
                    "physical_gpu":physical,"visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),"peak_allocated_bytes":torch.cuda.max_memory_allocated(),"scope":plan["scope"]})
    finally:
        if lock is not None:lock.close()
    return {"status":"complete"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=("self-test","prepare","evaluate"));p.add_argument("--physical-gpu",type=int,default=0);args=p.parse_args();torch.set_num_threads(4)
    result=self_test() if args.mode=="self-test" else prepare() if args.mode=="prepare" else evaluate(args.physical_gpu)
    print(json.dumps(result,indent=2),flush=True)
