"""E151 global routed/shared necessity and fixed random expert budgets; no training."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False);_p.add_argument("--physical-gpu",type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None,"",str(_early.physical_gpu)):raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"]=str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
import copy
from contextlib import contextmanager
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
import e150_native as n
from e150_partial_mask_test import FixedGate,Constant

RESULT=n.WB/"results/e151"
RAW=Path.home()/"mechpop_cache/e151_native_selectivity_necessity"
CONDITIONS=("native","routed_zero","shared_zero","random0","random1","random2")


def proof():return {**n.proof(),"e151_native.py":n.sha(__file__),"e150_partial_mask_test.py":n.sha(n.WB/"scripts/e150_partial_mask_test.py")}


class ZeroExpert(nn.Module):
    def forward(self,x):return torch.zeros_like(x)


@contextmanager
def suppress(model,which):
    originals=[layer.mlp for layer in model.model.layers]
    try:
        for layer,original in zip(model.model.layers,originals):
            if original.num_shared_experts!=1 or original.always_active_experts not in (None,[]):raise ValueError("Unexpected shared interface")
            block=copy.copy(original);block._modules=dict(original._modules)
            block._parameters=dict(original._parameters);block._buffers=dict(original._buffers)
            last=original.num_experts-1
            block.experts=nn.ModuleList([ZeroExpert() if ((i<last)==(which=="routed")) else expert
                                        for i,expert in enumerate(original.experts)])
            layer.mlp=block
        yield
    finally:
        for layer,original in zip(model.model.layers,originals):layer.mlp=original


def random_masks():
    masks=np.zeros((3,64,16,128),bool);masks[:,:,:,-1]=True
    for draw in range(3):
        rng=np.random.default_rng(151100+draw)
        for seq in range(64):
            for layer in range(16):masks[draw,seq,layer,rng.choice(127,31,replace=False)]=True
    return masks


@torch.no_grad()
def self_test():
    torch.set_num_threads(1)
    for source in range(2):
        cfg_cls,_,_=n.classes(source)
        module=__import__(f"codex_e150_source_{source}.modeling_emo",fromlist=["EmoSparseMoeBlock"])
        cfg=cfg_cls(hidden_size=4,intermediate_size=4,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False)
        block=module.EmoSparseMoeBlock(cfg,4,1,None);block.gate=FixedGate()
        block.experts=nn.ModuleList([Constant(v) for v in (2.,4.,8.,10.)])
        layer=nn.Module();layer.mlp=block;inner=nn.Module();inner.layers=nn.ModuleList([layer]);model=nn.Module();model.model=inner
        state=n.old.tensor_hash(model.state_dict());h=torch.ones(1,6,4);original=block(h)[0]
        assert torch.allclose(original,torch.full_like(original,10+8/7),atol=1e-6)
        with suppress(model,"routed"):assert torch.equal(model.model.layers[0].mlp(h)[0],torch.full_like(original,10))
        with suppress(model,"shared"):assert torch.allclose(model.model.layers[0].mlp(h)[0],torch.full_like(original,8/7),atol=1e-6)
        assert torch.equal(model.model.layers[0].mlp(h)[0],original)
        assert n.old.tensor_hash(model.state_dict())==state
    masks=random_masks();assert masks[:,:,:,-1].all() and np.all(masks.sum(-1)==32)
    n.write(RESULT/"self_test.json",{"status":"passed","CPU_only":True,"source_sha256":proof(),
        "routed_zero_known_answer":10,"shared_zero_known_answer":8/7,"source_restored_exact":True,"random_31_plus_shared_budget":True})
    return {"status":"passed"}


def prepare():
    test=n.read(RESULT/"self_test.json")
    if test["status"]!="passed" or test["source_sha256"]!=proof():raise ValueError("Matching known-answer tests required")
    source=n.read(n.RESULT/"manifest.json");plan=n.read(n.RESULT/"plan.json")
    assert source["status"]=="complete"
    RAW.mkdir(exist_ok=True,parents=True);path=RAW/"random_masks.npz";masks=random_masks()
    if path.exists():
        with np.load(path) as old:assert np.array_equal(old["masks"],masks)
    else:np.savez_compressed(path,masks=masks)
    result={"experiment":"E151","status":"prepared","source_sha256":proof(),"source_E150_manifest_sha256":n.sha(n.RESULT/"manifest.json"),
        "source_E150_plan_sha256":n.sha(n.RESULT/"plan.json"),"random_masks":{"path":str(path),"sha256":n.sha(path)},
        "random_draw_seeds":[151100,151101,151102],"conditions":list(CONDITIONS),"selected":plan["selected"],
        "scope":"Fixed 3 random-mask probes, not training seeds; source/input population is the same as E150."}
    n.old.immutable_json(RESULT/"plan.json",result)
    return {"status":"prepared"}


class Budget(n.old.Budget):
    def __init__(self):self.path,self.experiment,self.phase,self.limit=RESULT/"budget.json","e151","native_global_necessity_random_budgets",3600


@torch.no_grad()
def evaluate(physical):
    plan,assets=n.ready();own=n.read(RESULT/"plan.json");tests=n.read(RESULT/"self_test.json")
    if own["source_sha256"]!=proof() or tests["source_sha256"]!=proof():raise ValueError("Frozen E151 source differs")
    if n.sha(n.RESULT/"manifest.json")!=own["source_E150_manifest_sha256"] or n.sha(n.RESULT/"plan.json")!=own["source_E150_plan_sha256"]:raise ValueError("E150 source changed")
    if n.sha(own["random_masks"]["path"])!=own["random_masks"]["sha256"]:raise ValueError("Random masks changed")
    with np.load(plan["path"]) as f:held=f["held"].copy();valid=f["held_mask"].copy();cal=f["cal"][:2,:129].copy();cv=f["cal_mask"][:2,:128].copy()
    with np.load(own["random_masks"]["path"]) as f:masks=f["masks"].copy()
    suffix=valid&(np.arange(512)[None,:]>=127)
    pre=n.read(n.RESULT/"preflight.json");lock=None
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical);models=[]
            for source in range(2):
                budget.check();model=n.load_bf16(source);models.append(model)
                cp=pre["models"][str(source)];p=cp["cal_BF16_logits"]
                assert n.sha(p["path"])==p["sha256"] and n.old.tensor_hash(n.buffers(model))==cp["buffer_hash"]
                with np.load(p["path"]) as f:reference=torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                ids=torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
                am=torch.cat([torch.ones((2,1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(cv).to("cuda:0")],1)
                if not torch.equal(n.fwd(model,ids[:,:-1],am[:,:-1]),reference):raise ValueError("Native calibration replay differs")
                del ids,am,reference
            before=[n.old.tensor_hash(m.state_dict()) for m in models];before_buffers=[n.old.tensor_hash(n.buffers(m)) for m in models]
            values=np.empty((2,6,64,512,4),np.float32);coverage=np.empty((2,3,64,16,3),np.float32)
            for start in range(0,64,4):
                budget.check();ids=torch.from_numpy(held[start:start+4].astype(np.int64)).to("cuda:0")
                am=torch.cat([torch.ones((len(ids),1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(valid[start:start+4]).to("cuda:0")],1)
                for source,model in enumerate(models):
                    with n.restricted.routing_coverage(model,masks[:,start:start+4],suffix[start:start+4]) as captured:
                        reference=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                    coverage[source,:,start:start+4]=captured
                    values[source,0,start:start+4]=n.old.prediction_metrics(reference,reference,ids[:,1:]).cpu().numpy()
                    for index,which in ((1,"routed"),(2,"shared")):
                        budget.check()
                        with suppress(model,which):q=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                        values[source,index,start:start+4]=n.old.prediction_metrics(reference,q,ids[:,1:]).cpu().numpy();del q
                    for draw in range(3):
                        budget.check()
                        with n.restricted.restricted_gates(model,masks[draw,start:start+4]):q=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                        values[source,3+draw,start:start+4]=n.old.prediction_metrics(reference,q,ids[:,1:]).cpu().numpy();del q
                    del reference
                del ids,am
                n.old.emit("E151_batch",sequences=start+4,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            if any(n.old.tensor_hash(m.state_dict())!=h for m,h in zip(models,before)):raise ValueError("Source parameters mutated")
            if any(n.old.tensor_hash(n.buffers(m))!=h for m,h in zip(models,before_buffers)):raise ValueError("Source buffers mutated")
            base=n.read(n.RESULT/"manifest.json")["raw"]
            if n.sha(base["path"])!=base["sha256"]:raise ValueError("E150 raw changed")
            with np.load(base["path"]) as f:
                for source,index in ((0,0),(1,15)):
                    if not np.array_equal(values[source,0,:,:,0],f["metrics"][index,:,:,0,0]):raise ValueError("Native held NLL differs from E150")
            path=RAW/"metrics.npz"
            if path.exists():raise ValueError("Refusing to replace E151 raw")
            np.savez_compressed(path,metrics=values,coverage=coverage,valid=valid,suffix_valid=suffix,conditions=np.array(CONDITIONS),fields=np.array(n.old.METRICS))
            result={"experiment":"E151","status":"complete","source_sha256":proof(),"plan_sha256":n.sha(RESULT/"plan.json"),
                "raw":{"path":str(path),"sha256":n.sha(path),"size_bytes":path.stat().st_size},"controls":{"calibration_replay_exact":True,
                "source_parameters_and_buffers_unchanged":True,"native_held_NLL_exact_E150":True},"parameter_hashes":before,"buffer_hashes":before_buffers,
                "physical_gpu":physical,"visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),"peak_allocated_bytes":torch.cuda.max_memory_allocated(),
                "scope":"Global necessity and fixed random budgets in the same mature pair; no new training or independent population."}
            n.write(RESULT/"manifest.json",result)
    finally:
        if lock is not None:lock.close()
    return {"status":"complete"}


def analyze():
    m=n.read(RESULT/"manifest.json");plan=n.read(RESULT/"plan.json");prior=n.read(n.RESULT/"manifest.json")
    if m["status"]!="complete" or m["source_sha256"]!=proof() or n.sha(m["raw"]["path"])!=m["raw"]["sha256"]:raise ValueError("Sealed E151 data required")
    with np.load(m["raw"]["path"]) as f:
        full=np.stack([[n.data.masked_mean(v.astype(float),f["valid"]) for v in source] for source in f["metrics"]])
        suffix=np.stack([[n.data.masked_mean(v.astype(float),f["suffix_valid"]) for v in source] for source in f["metrics"]])
        coverage=f["coverage"].astype(float).copy()
    if n.sha(prior["raw"]["path"])!=prior["raw"]["sha256"]:raise ValueError("E150 comparison raw differs")
    with np.load(prior["raw"]["path"]) as f:
        prefixes=np.stack([[n.data.masked_mean(f["restricted_metrics"][selector,index].astype(float),f["suffix_valid"]) for selector in range(2)] for index in (0,15)])
    stats=lambda x:n.input_stats(np.asarray(x),plan["selected"],151001)
    result={"experiment":"E151","status":"complete","sources":{},"B_minus_A":{},"source_sha256":proof(),
            "scope":"Input-file intervals conditional on three fixed random probes; not training seeds or a random-mask population CI."}
    for source,name in enumerate("AB"):
        record={"conditions":{},"random_vs_prefix":{}}
        for i,condition in enumerate(CONDITIONS):
            record["conditions"][condition]={"full_NLL":stats(full[source,i,:,0]),"full_delta_NLL":stats(full[source,i,:,0]-full[source,0,:,0]),
                "full_KL":stats(full[source,i,:,1]),"suffix_delta_NLL":stats(suffix[source,i,:,0]-suffix[source,0,:,0]),"suffix_KL":stats(suffix[source,i,:,1])}
        for selector,label in enumerate("AB"):
            record["random_vs_prefix"][label]={"random_mean_minus_prefix_NLL":stats(suffix[source,3:,:,0].mean(0)-prefixes[source,selector,:,0]),
                "random_mean_minus_prefix_KL":stats(suffix[source,3:,:,1].mean(0)-prefixes[source,selector,:,1])}
        record["random_mean"]={"suffix_delta_NLL":stats(suffix[source,3:,:,0].mean(0)-suffix[source,0,:,0]),
            "suffix_KL":stats(suffix[source,3:,:,1].mean(0)),"top7_support_retained":stats(coverage[source,:,:, :,0].mean((0,2)))}
        result["sources"][name]=record
    for index,label in ((1,"routed_zero"),(2,"shared_zero")):
        result["B_minus_A"][label]={"full_delta_NLL":stats((full[1,index,:,0]-full[1,0,:,0])-(full[0,index,:,0]-full[0,0,:,0])),
            "full_KL":stats(full[1,index,:,1]-full[0,index,:,1])}
    result["B_minus_A"]["random_mean"]={"suffix_delta_NLL":stats((suffix[1,3:,:,0].mean(0)-suffix[1,0,:,0])-(suffix[0,3:,:,0].mean(0)-suffix[0,0,:,0])),
        "suffix_KL":stats(suffix[1,3:,:,1].mean(0)-suffix[0,3:,:,1].mean(0))}
    n.write(RESULT/"summary.json",result)
    print(json.dumps({"status":"complete","sources":{k:{"routed_zero":v["conditions"]["routed_zero"],"shared_zero":v["conditions"]["shared_zero"],"random_mean":v["random_mean"],"random_vs_prefix":v["random_vs_prefix"]} for k,v in result["sources"].items()},"B_minus_A":result["B_minus_A"]},indent=2))
    return {"status":"complete"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=("self-test","prepare","evaluate","analyze"));p.add_argument("--physical-gpu",type=int,default=0)
    args=p.parse_args();torch.set_num_threads(4)
    out=self_test() if args.mode=="self-test" else prepare() if args.mode=="prepare" else evaluate(args.physical_gpu) if args.mode=="evaluate" else analyze()
    if args.mode!="analyze":print(json.dumps(out,indent=2),flush=True)
