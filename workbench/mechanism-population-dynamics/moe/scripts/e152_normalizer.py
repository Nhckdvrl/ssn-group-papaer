"""E152 fixed-subset normalizer counterfactual in native EMO blocks."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False);_p.add_argument("--physical-gpu",type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None,"",str(_early.physical_gpu)):raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"]=str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
from contextlib import contextmanager
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import e150_native as n
from e150_partial_mask_test import FixedGate,Constant

RESULT=n.WB/"results/e152"
RAW=Path.home()/"mechpop_cache/e152_native_normalizer_counterfactual"
MASKS=("prefixA","prefixB","random0","random1","random2")
RULES=("pool","full")
CONDITIONS=("native",)+tuple(f"{mask}_{rule}" for mask in MASKS for rule in RULES)


def proof():
    return {**n.proof(),"e152_normalizer.py":n.sha(__file__),
            "e150_partial_mask_test.py":n.sha(n.WB/"scripts/e150_partial_mask_test.py")}


class NormalizerBlock(nn.Module):
    """Native dispatch/sum; fixed available slots, two denominator rules."""
    def __init__(self,block,keep,rule,valid=None,trace=None,layer=0):
        super().__init__()
        if block.num_shared_experts!=1 or block.always_active_experts not in (None,[]) or block.norm_topk_prob:
            raise ValueError("Audited routed/shared no-renorm interface required")
        self.gate=block.gate;self.experts=nn.ModuleList(list(block.experts))
        self.top_k,self.num_experts,self.num_shared_experts=block.top_k,block.num_experts,1
        self.norm_topk_prob=False;self.always_active_experts=None
        self.register_buffer("keep",keep,persistent=False)
        self.rule,self.valid,self.trace,self.layer=rule,valid,trace,layer
        self.last_selected=None
    def forward(self,hidden_states):
        batch,length,width=hidden_states.shape
        hidden=hidden_states.view(-1,width);logits=self.gate(hidden)
        allowed=self.keep[:,None,:].expand(batch,length,self.num_experts).reshape(-1,self.num_experts)
        masked=logits.masked_fill(~allowed,-torch.inf)
        pool_probability=F.softmax(masked[:,:-1],dim=1,dtype=torch.float32)
        selected_weight,selected=pool_probability.topk(self.top_k-1,-1)
        if self.rule=="full":
            selected_weight=F.softmax(logits[:,:-1],dim=1,dtype=torch.float32).gather(-1,selected)
        elif self.rule!="pool":raise ValueError("Unknown denominator rule")
        shared_weight,shared_index=F.softmax(logits[:,-1:],dim=1,dtype=torch.float32).topk(1,-1)
        weights=torch.cat((selected_weight,shared_weight),dim=1).to(hidden.dtype)
        selected=torch.cat((selected,shared_index+self.num_experts-1),dim=1)
        self.last_selected=selected.detach()
        if self.trace is not None:
            applied=weights[:,:-1].float().sum(-1).reshape(batch,length)
            self.trace[:,self.layer]=((applied*self.valid).sum(1)/self.valid.sum(1)).cpu().numpy()
        output=torch.zeros((batch*length,width),dtype=hidden.dtype,device=hidden.device)
        expert_mask=F.one_hot(selected,num_classes=self.num_experts).permute(2,1,0)
        for physical,expert in enumerate(self.experts):
            slot,row=torch.where(expert_mask[physical])
            value=expert(hidden[None,row].reshape(-1,width))*weights[row,slot,None]
            output.index_add_(0,row,value.to(hidden.dtype))
        return output.reshape(batch,length,width),masked if self.rule=="pool" else logits


@contextmanager
def intervene(model,keep,rule,valid=None):
    device=next(model.parameters()).device
    keep=torch.as_tensor(keep,dtype=torch.bool,device=device)
    if not bool(keep[:,:,-1].all()):raise ValueError("Shared slot must remain available")
    valid=None if valid is None else torch.as_tensor(valid,dtype=torch.float32,device=device)
    trace=None if valid is None else np.empty((len(keep),len(model.model.layers)),np.float32)
    originals=[layer.mlp for layer in model.model.layers]
    try:
        for i,(layer,block) in enumerate(zip(model.model.layers,originals)):
            layer.mlp=NormalizerBlock(block,keep[:,i],rule,valid,trace,i)
        yield trace
    finally:
        for layer,block in zip(model.model.layers,originals):layer.mlp=block


@torch.no_grad()
def self_test():
    torch.manual_seed(152);torch.set_num_threads(1)
    for source in range(2):
        cfg_cls,model_cls,_=n.classes(source)
        module=__import__(f"codex_e150_source_{source}.modeling_emo",fromlist=["EmoSparseMoeBlock"])
        cfg=cfg_cls(hidden_size=4,intermediate_size=4,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False)
        block=module.EmoSparseMoeBlock(cfg,4,1,None);block.gate=FixedGate()
        block.experts=nn.ModuleList([Constant(v) for v in (2.,5.,8.,10.)])
        h=torch.ones(1,3,4);keep=torch.tensor([[False,True,True,True]])
        assert torch.allclose(block(h)[0],torch.full_like(h,10+8/7),atol=2e-6)
        pool=NormalizerBlock(block,keep,"pool");full=NormalizerBlock(block,keep,"full")
        assert torch.allclose(pool(h)[0],torch.full_like(h,10+10/3),atol=2e-6)
        assert torch.allclose(full(h)[0],torch.full_like(h,10+10/7),atol=2e-6)
        assert torch.equal(pool.last_selected,full.last_selected)
        for dtype in (torch.float32,torch.bfloat16):
            c=cfg_cls(vocab_size=64,hidden_size=16,intermediate_size=8,num_hidden_layers=2,num_attention_heads=2,num_key_value_heads=2,
                      num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False,pad_token_id=63,eos_token_id=62,
                      max_position_embeddings=32,attention_dropout=0.,output_router_logits=False)
            c._attn_implementation="eager";model=model_cls(c).to(dtype=dtype).eval()
            ids=torch.randint(0,62,(2,7));am=torch.ones_like(ids)
            before=n.old.tensor_hash(model.state_dict());buf=n.old.tensor_hash(n.buffers(model))
            reference=n.fwd(model,ids,am);all_slots=np.ones((2,2,4),bool)
            for rule in RULES:
                with intervene(model,all_slots,rule):assert torch.equal(n.fwd(model,ids,am),reference)
            partial=all_slots.copy();partial[0,:,0]=False;partial[1,:,1]=False
            with n.restricted.restricted_gates(model,partial):expected=n.fwd(model,ids,am)
            with intervene(model,partial,"pool"):assert torch.equal(n.fwd(model,ids,am),expected)
            with intervene(model,partial,"full"):assert torch.isfinite(n.fwd(model,ids,am)).all()
            assert n.old.tensor_hash(model.state_dict())==before and n.old.tensor_hash(n.buffers(model))==buf
    n.write(RESULT/"self_test.json",{"status":"passed","CPU_only":True,"source_sha256":proof(),"checks":{
        "constant_expert_pool_full_oracles":True,"same_input_selected_indices_equal":True,"both_dtypes_all_slot_native_exact":True,
        "pool_partial_matches_native_hook_exact":True,"source_parameters_buffers_restored":True}})
    return {"status":"passed"}


def prepare():
    tests=n.read(RESULT/"self_test.json")
    if tests["status"]!="passed" or tests["source_sha256"]!=proof():raise ValueError("Matching known-answer checks required")
    prior=n.read(n.RESULT/"manifest.json");random=n.read(n.WB/"results/e151/plan.json")
    if n.sha(prior["raw"]["path"])!=prior["raw"]["sha256"] or n.sha(random["random_masks"]["path"])!=random["random_masks"]["sha256"]:raise ValueError("Sealed old masks changed")
    with np.load(prior["raw"]["path"]) as f:prefixes=f["prefix_keeps"].copy()
    with np.load(random["random_masks"]["path"]) as f:r=f["masks"].copy()
    masks=np.concatenate((prefixes,r),axis=0)
    assert masks.shape==(5,64,16,128) and np.all(masks.sum(-1)==32) and masks[:,:,:,-1].all()
    RAW.mkdir(parents=True,exist_ok=True);path=RAW/"masks.npz"
    if path.exists():
        with np.load(path) as f:assert np.array_equal(f["masks"],masks)
    else:np.savez_compressed(path,masks=masks)
    plan={"experiment":"E152","status":"prepared","source_sha256":proof(),"E150_manifest_sha256":n.sha(n.RESULT/"manifest.json"),
        "E151_manifest_sha256":n.sha(n.WB/"results/e151/manifest.json"),"E150_input_plan_sha256":n.sha(n.RESULT/"plan.json"),
        "masks":{"path":str(path),"sha256":n.sha(path)},"mask_order":list(MASKS),"rule_order":list(RULES),"conditions":list(CONDITIONS),
        "selected":n.read(n.RESULT/"plan.json")["selected"],"scope":"Same old masks/inputs, new denominator rule; no re-selection or new training."}
    n.old.immutable_json(RESULT/"plan.json",plan)
    return {"status":"prepared"}


class Budget(n.old.Budget):
    def __init__(self):self.path,self.experiment,self.phase,self.limit=RESULT/"budget.json","e152","fixed_subset_denominator_rules",3600


@torch.no_grad()
def evaluate(physical):
    inp,assets=n.ready();own=n.read(RESULT/"plan.json");tests=n.read(RESULT/"self_test.json")
    if own["source_sha256"]!=proof() or tests["source_sha256"]!=proof():raise ValueError("Frozen code differs")
    for p,k in ((n.RESULT/"manifest.json","E150_manifest_sha256"),(n.WB/"results/e151/manifest.json","E151_manifest_sha256"),(n.RESULT/"plan.json","E150_input_plan_sha256")):
        if n.sha(p)!=own[k]:raise ValueError("Prior sources changed")
    if n.sha(own["masks"]["path"])!=own["masks"]["sha256"]:raise ValueError("Fixed masks changed")
    with np.load(inp["path"]) as f:held=f["held"].copy();valid=f["held_mask"].copy();cal=f["cal"][:2,:129].copy();cv=f["cal_mask"][:2,:128].copy()
    with np.load(own["masks"]["path"]) as f:masks=f["masks"].copy()
    suffix=valid&(np.arange(512)[None,:]>=127);pre=n.read(n.RESULT/"preflight.json");lock=None
    controls={"native_cal_replay":True,"both_full_slot_rules_native_exact":True,"pool_cal_matches_old_hook":True}
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical);models=[]
            for source in range(2):
                budget.check();model=n.load_bf16(source);models.append(model)
                record=pre["models"][str(source)];raw=record["cal_BF16_logits"]
                if n.sha(raw["path"])!=raw["sha256"] or n.old.tensor_hash(n.buffers(model))!=record["buffer_hash"]:raise ValueError("Cal/buffers changed")
                with np.load(raw["path"]) as f:reference=torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                ids=torch.from_numpy(cal.astype(np.int64)).to("cuda:0");am=torch.cat((torch.ones((2,1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(cv).to("cuda:0")),1)
                if not torch.equal(n.fwd(model,ids[:,:-1],am[:,:-1]),reference):raise ValueError("Native calibration replay differs")
                for rule in RULES:
                    with intervene(model,np.ones((2,16,128),bool),rule):actual=n.fwd(model,ids[:,:-1],am[:,:-1])
                    if not torch.equal(actual,reference):raise ValueError("Full-slot rule changes native calibration")
                partial=n.restricted.prefix_keep(model,ids[:,:128],32)
                with n.restricted.restricted_gates(model,partial):expected=n.fwd(model,ids[:,:-1],am[:,:-1])
                with intervene(model,partial,"pool"):actual=n.fwd(model,ids[:,:-1],am[:,:-1])
                if not torch.equal(actual,expected):raise ValueError("Pool implementation fails exact old calibration")
                del ids,am,reference,actual,expected
            before=[n.old.tensor_hash(m.state_dict()) for m in models];buffers=[n.old.tensor_hash(n.buffers(m)) for m in models]
            values=np.empty((2,11,64,512,4),np.float32);gate_sum=np.empty((2,10,64,16),np.float32)
            for start in range(0,64,4):
                budget.check();ids=torch.from_numpy(held[start:start+4].astype(np.int64)).to("cuda:0")
                am=torch.cat((torch.ones((len(ids),1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(valid[start:start+4]).to("cuda:0")),1)
                for source,model in enumerate(models):
                    reference=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                    values[source,0,start:start+4]=n.old.prediction_metrics(reference,reference,ids[:,1:]).cpu().numpy()
                    for mask in range(5):
                        for rule_index,rule in enumerate(RULES):
                            budget.check();index=2*mask+rule_index
                            with intervene(model,masks[mask,start:start+4],rule,suffix[start:start+4]) as trace:
                                q=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                            values[source,index+1,start:start+4]=n.old.prediction_metrics(reference,q,ids[:,1:]).cpu().numpy()
                            gate_sum[source,index,start:start+4]=trace;del q
                    del reference
                del ids,am;n.old.emit("E152_batch",sequences=start+4,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            if any(n.old.tensor_hash(m.state_dict())!=h for m,h in zip(models,before)):raise ValueError("Source parameters mutated")
            if any(n.old.tensor_hash(n.buffers(m))!=h for m,h in zip(models,buffers)):raise ValueError("Source buffers mutated")
            e150=n.read(n.RESULT/"manifest.json")["raw"];e151=n.read(n.WB/"results/e151/manifest.json")["raw"]
            if n.sha(e150["path"])!=e150["sha256"] or n.sha(e151["path"])!=e151["sha256"]:raise ValueError("Old readout raw changed")
            with np.load(e150["path"]) as a,np.load(e151["path"]) as b:
                for source,corner in ((0,0),(1,15)):
                    if not np.array_equal(values[source,0,:,:,0],a["metrics"][corner,:,:,0,0]):raise ValueError("Native NLL changed")
                    for mask in range(5):
                        old=a["restricted_metrics"][mask,corner,:,:,0] if mask<2 else b["metrics"][source,mask+1,:,:,0]
                        if not np.array_equal(values[source,2*mask+1,:,:,0],old):raise ValueError(f"Pool held NLL differs: source{source},mask{mask}")
            controls.update(native_held_NLL_exact=True,all_pool_held_NLL_exact_old=True,source_parameters_and_buffers_unchanged=True)
            path=RAW/"metrics.npz"
            if path.exists():raise ValueError("Refusing to replace readout")
            np.savez_compressed(path,metrics=values,applied_gate_sum=gate_sum,valid=valid,suffix_valid=suffix,conditions=np.array(CONDITIONS),fields=np.array(n.old.METRICS))
            result={"experiment":"E152","status":"complete","source_sha256":proof(),"plan_sha256":n.sha(RESULT/"plan.json"),
                "raw":{"path":str(path),"sha256":n.sha(path),"size_bytes":path.stat().st_size},"controls":controls,"source_parameter_hashes":before,
                "source_buffer_hashes":buffers,"physical_gpu":physical,"visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),
                "peak_allocated_bytes":torch.cuda.max_memory_allocated(),"scope":"Global denominator-rule intervention with fixed old masks; later H/routes may change. Actual BF16, no new training."}
            n.write(RESULT/"manifest.json",result)
    finally:
        if lock is not None:lock.close()
    return {"status":"complete"}


def analyze():
    m=n.read(RESULT/"manifest.json");plan=n.read(RESULT/"plan.json")
    if m["status"]!="complete" or m["source_sha256"]!=proof() or n.sha(m["raw"]["path"])!=m["raw"]["sha256"]:raise ValueError("Sealed results required")
    with np.load(m["raw"]["path"]) as f:
        a=np.stack([[n.data.masked_mean(v.astype(float),f["suffix_valid"]) for v in source] for source in f["metrics"]])
        g=f["applied_gate_sum"].astype(float).mean(-1)
    stats=lambda x:n.input_stats(np.asarray(x),plan["selected"],152001)
    result={"experiment":"E152","status":"complete","sources":{},"B_minus_A":{},"rule_difference_in_difference":{},
        "scope":"Suffix sequence means and input-file CIs; fixed3random probes, one public protocol pair, not semantic units or training populations."}
    penalties=a[:,:,:,0]-a[:,0:1,:,0]
    for source,label in enumerate("AB"):
        record={"native_suffix_NLL":stats(a[source,0,:,0]),"masks":{},"random_mean":{},"selection_advantage":{}}
        for j,mask in enumerate(MASKS):
            cases={}
            for r,rule in enumerate(RULES):
                k=1+2*j+r
                cases[rule]={"NLL":stats(a[source,k,:,0]),"delta_NLL":stats(penalties[source,k]),
                    "native_to_variant_KL":stats(a[source,k,:,1]),"variant_to_native_KL":stats(a[source,k,:,2]),
                    "applied_R_mass":stats(g[source,k-1])}
            lo,hi=1+2*j,2+2*j
            cases["full_minus_pool"]={"NLL":stats(a[source,hi,:,0]-a[source,lo,:,0]),"KL":stats(a[source,hi,:,1]-a[source,lo,:,1])}
            record["masks"][mask]=cases
        for r,rule in enumerate(RULES):
            indices=[1+2*j+r for j in range(2,5)];random=a[source,indices].mean(0)
            record["random_mean"][rule]={"delta_NLL":stats(random[:,0]-a[source,0,:,0]),"KL":stats(random[:,1])}
            record["selection_advantage"][rule]={mask:{"NLL":stats(random[:,0]-a[source,1+2*j+r,:,0]),
                "KL":stats(random[:,1]-a[source,1+2*j+r,:,1])} for j,mask in enumerate(MASKS[:2])}
        result["sources"][label]=record
    for j,mask in enumerate(MASKS):
        result["B_minus_A"][mask]={}
        for r,rule in enumerate(RULES):
            k=1+2*j+r
            result["B_minus_A"][mask][rule]={"delta_NLL":stats(penalties[1,k]-penalties[0,k]),"KL":stats(a[1,k,:,1]-a[0,k,:,1]),"absolute_NLL":stats(a[1,k,:,0]-a[0,k,:,0])}
        lo,hi=1+2*j,2+2*j
        result["rule_difference_in_difference"][mask]={"NLL":stats((a[1,hi,:,0]-a[1,lo,:,0])-(a[0,hi,:,0]-a[0,lo,:,0])),
            "KL":stats((a[1,hi,:,1]-a[1,lo,:,1])-(a[0,hi,:,1]-a[0,lo,:,1]))}
    result["own_prefix_B_minus_A"]={rule:{"delta_NLL":stats(penalties[1,3+r]-penalties[0,1+r]),"KL":stats(a[1,3+r,:,1]-a[0,1+r,:,1])} for r,rule in enumerate(RULES)}
    n.write(RESULT/"summary.json",result)
    return {"status":"complete","own_prefix_B_minus_A":result["own_prefix_B_minus_A"],
            "random_mean":{k:v["random_mean"] for k,v in result["sources"].items()}}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=("self-test","prepare","evaluate","analyze"));p.add_argument("--physical-gpu",type=int,default=0)
    args=p.parse_args();torch.set_num_threads(4)
    out=self_test() if args.mode=="self-test" else prepare() if args.mode=="prepare" else evaluate(args.physical_gpu) if args.mode=="evaluate" else analyze()
    print(json.dumps(out,indent=2),flush=True)
