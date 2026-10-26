"""E150: mature public protocol endpoints, dense/router/routed/shared source cube."""
from __future__ import annotations
import argparse
import os
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--physical-gpu", type=int, default=0)
_early, _ = _parser.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "", str(_early.physical_gpu)):
    raise ValueError("Requested physical device and visibility differ")
os.environ["CUDA_VISIBLE_DEVICES"] = str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"

import copy
import importlib
import itertools
import json
import re
import sys
import types
from pathlib import Path
import numpy as np
import torch
from torch import nn
import transformers
import e144145_common as old
from e144145_analyze import input_stats
import e150_data as data

torch.use_deterministic_algorithms(True)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
RESULT, RAW, WB = data.RESULT, data.RAW, data.WB
NAMES = ("StdMoE_1b14b_1T", "StdMoE_1b14b_1T_EmoAnnealed")
FACTORS = ("dense_backbone", "all_routers", "routed_experts", "shared_experts")
CASES = tuple(itertools.product(range(2), repeat=4))
read, write, sha = old.read, old.write, old.sha


def assets(complete=False):
    manifest = read(RESULT / ("asset_manifest.json" if complete else "metadata.json"))
    if manifest["status"] != ("complete" if complete else "metadata_complete"):
        raise ValueError("Complete pinned asset stage required")
    for model in manifest["models"].values():
        for filename, proof in model["files"].items():
            path = Path(proof["path"])
            if path.stat().st_size != proof["size_bytes"]: raise ValueError("Pinned asset size changed")
            # Full large-file SHA was streamed and compared to public LFS IDs by
            # the asset stage. Recheck small executable/config files here.
            if not filename.endswith(".safetensors") and sha(path) != proof["sha256"]:
                raise ValueError("Pinned model code/config/tokenizer changed")
    return manifest


def proof():
    result = {name: sha(WB / "scripts" / name) for name in ("e150_native.py", "e150_data.py", "e144145_common.py", "e123_frozen_moe.py")}
    for name, record in assets()["models"].items():
        for file in ("configuration_emo.py", "modeling_emo.py", "config.json"):
            result[name+"/"+file] = record["files"][file]["sha256"]
    return result


def classes(source):
    root = Path(assets()["models"][NAMES[source]]["path"])
    namespace = f"codex_e150_source_{source}"
    if namespace not in sys.modules:
        package = types.ModuleType(namespace); package.__path__ = [str(root)]
        sys.modules[namespace] = package
    config = importlib.import_module(namespace+".configuration_emo").EmoConfig
    model = importlib.import_module(namespace+".modeling_emo").EmoForCausalLM
    return config, model, root


def original_blocks(models):
    return [[layer.mlp for layer in model.model.layers] for model in models]


def assemble(models, blocks, case):
    dense, gate, routed, shared = case
    model = models[dense]
    for layer, target in enumerate(model.model.layers):
        template = blocks[dense][layer]
        if template.num_shared_experts != 1 or template.always_active_experts not in (None, []):
            raise ValueError("Expected the audited last-slot shared-expert interface")
        # The original forward and its metadata remain intact. Copy only the
        # module registries; source blocks and their ModuleLists are never edited.
        block = copy.copy(template)
        block._modules = dict(template._modules)
        block._parameters = dict(template._parameters)
        block._buffers = dict(template._buffers)
        block.gate = blocks[gate][layer].gate
        block.experts = nn.ModuleList(list(blocks[routed][layer].experts[:-1])+[blocks[shared][layer].experts[-1]])
        target.mlp = block
    return model


def restore(models, blocks):
    for model, group in zip(models, blocks):
        for layer, block in zip(model.model.layers, group): layer.mlp = block


def group_index(name, shared_slot):
    if ".mlp.gate." in name: return 1
    match = re.search(r"\.mlp\.experts\.(\d+)\.", name)
    if match: return 3 if int(match.group(1)) == shared_slot else 2
    return 0


def buffers(model): return {k:v.detach().cpu().clone() for k,v in model.named_buffers()}


def fwd(model, ids, mask):
    return model(input_ids=ids, attention_mask=mask, use_cache=False, output_router_logits=False, return_dict=True).logits


def interaction(values, axes, fixed):
    others = [i for i in range(4) if i not in axes]
    result = np.zeros_like(next(iter(values.values())), dtype=float)
    for settings in itertools.product(range(2), repeat=len(axes)):
        case = [0]*4
        for axis, value in zip(axes, settings): case[axis] = value
        for axis, value in zip(others, fixed): case[axis] = value
        result += (-1)**(len(axes)-sum(settings))*values[tuple(case)]
    return result


@torch.no_grad()
def self_test():
    torch.manual_seed(150); torch.set_num_threads(1)
    models = []
    for source in range(2):
        cfg_cls, cls, _ = classes(source)
        cfg = cfg_cls(vocab_size=64, hidden_size=16, intermediate_size=8, num_hidden_layers=2,
                      num_attention_heads=2, num_key_value_heads=2, num_experts=4, num_experts_per_tok=2,
                      num_shared_experts=1, norm_topk_prob=False, pad_token_id=63, eos_token_id=62,
                      max_position_embeddings=32, attention_dropout=0., output_router_logits=False)
        cfg._attn_implementation = "eager"
        models.append(cls(cfg).bfloat16().eval())
    states = [copy.deepcopy(m.state_dict()) for m in models]
    saved_buffers = [old.tensor_hash(buffers(m)) for m in models]
    blocks = original_blocks(models)
    ids = torch.randint(0, 62, (2, 7)); mask = torch.ones_like(ids); mask[1, 5:] = 0
    native = [fwd(m, ids, mask).clone() for m in models]
    for case in CASES:
        model = assemble(models, blocks, case)
        for name, value in model.named_parameters():
            assert torch.equal(value, states[case[group_index(name, 3)]][name]), (case, name)
        value = fwd(model, ids, mask)
        if len(set(case)) == 1: assert torch.equal(value, native[case[0]])
    restore(models, blocks)
    for source, model in enumerate(models):
        assert all(torch.equal(value, states[source][name]) for name,value in model.state_dict().items())
        assert old.tensor_hash(buffers(model)) == saved_buffers[source]
    y = {c: np.array(1+2*c[0]+3*c[1]+5*c[2]+7*c[3]+11*c[1]*c[2]+13*c[2]*c[3]+17*np.prod(c)) for c in CASES}
    assert interaction(y, (1,2), (0,0)) == 11
    assert np.mean([interaction(y, (1,2), f) for f in itertools.product(range(2), repeat=2)]) == 15.25
    assert interaction(y, (0,1,2,3), ()) == 17
    assert np.array_equal(data.masked_mean(np.array([[1.,3.,np.nan],[2.,np.nan,np.nan]]), [[1,1,0],[1,0,0]]), [2.,2.])
    # Verify IDs above 16 bits survive the new tokenizer storage contract.
    example = np.array([100277,100351], dtype=np.uint32)
    assert example.tolist() == [100277,100351]
    result = {"status":"passed", "CPU_only":True, "source_sha256":proof(), "checks":{
        "all_16_parameter_sources":True, "native_corners_exact":True, "source_parameters_and_buffers_unchanged":True,
        "two_and_four_way_known_answers":True, "masked_variable_length_known_answer":True, "uint32_token_storage":True}}
    write(RESULT / "self_test.json", result)
    return {"status":"passed"}


class Budget(old.Budget):
    def __init__(self, phase):
        self.path, self.experiment, self.phase, self.limit = RESULT / "budget.json", "e150", phase, 7200


def ready():
    test = read(RESULT / "self_test.json")
    if test["status"] != "passed" or test["source_sha256"] != proof(): raise ValueError("Matching CPU source tests required")
    plan = read(RESULT / "plan.json")
    if plan["data_source_sha256"] != sha(data.__file__) or sha(plan["path"]) != plan["sha256"]: raise ValueError("Frozen input bytes/code differ")
    return plan, assets(complete=True)


def load_fp32(source):
    cfg_cls, cls, root = classes(source)
    cfg = cfg_cls.from_json_file(root / "config.json")
    return cls.from_pretrained(root, config=cfg, dtype=torch.float32, local_files_only=True,
                               attn_implementation="sdpa").to("cuda:0").eval().requires_grad_(False)


def load_bf16(source):
    # A single canonical conversion also casts nonpersistent RoPE buffers.
    # Sequential loads peak near 27.14 + 54.27 GB, before reducing to 2 x BF16.
    model = load_fp32(source).bfloat16()
    torch.cuda.empty_cache()
    return model


class Zero(nn.Module):
    def __init__(self, gate): super().__init__(); self.gate = gate
    def forward(self, hidden): return torch.zeros_like(hidden), self.gate(hidden.reshape(-1,hidden.shape[-1]))


@torch.no_grad()
def preflight(physical):
    plan, asset = ready()
    with np.load(plan["path"]) as raw: cal = raw["cal"][:2,:129].copy(); valid = raw["cal_mask"][:2,:128].copy()
    lock = None; result = {"experiment":"E150", "status":"partial", "source_sha256":proof(), "models":{}}
    try:
        with Budget("mature_native_calibration_preflight") as budget:
            lock = old.gpu_lock(physical)
            ids = torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            mask = torch.cat((torch.ones((2,1),device="cuda:0",dtype=torch.bool),torch.from_numpy(valid).to("cuda:0")),1)
            for source in range(2):
                budget.check(); model = load_fp32(source)
                p32 = fwd(model, ids[:,:-1], mask[:,:-1]).float().log_softmax(-1)
                model.bfloat16(); torch.cuda.empty_cache()
                logits = fwd(model, ids[:,:-1], mask[:,:-1])
                again = fwd(model, ids[:,:-1], mask[:,:-1])
                if not torch.equal(logits, again): raise ValueError("BF16 native calibration replay differs")
                p16 = logits.float().log_softmax(-1)
                precision = data.masked_mean(old.prediction_metrics(p32,p16,ids[:,1:]).cpu().numpy(), valid)
                original = model.model.layers[9].mlp
                model.model.layers[9].mlp = Zero(original.gate)
                zero = fwd(model, ids[:,:-1], mask[:,:-1]).float().log_softmax(-1)
                model.model.layers[9].mlp = original
                positive = data.masked_mean(old.prediction_metrics(p16,zero,ids[:,1:]).cpu().numpy(),valid)
                if float((p16-zero).abs().max()) == 0: raise ValueError("L9 zero failed to change the calibration predictor")
                path = RAW / f"cal_source_{source}.npz"
                if path.exists(): raise ValueError("Refusing to replace native cal proof")
                np.savez_compressed(path, logits=logits.contiguous().view(torch.uint16).cpu().numpy())
                result["models"][str(source)] = {"source":NAMES[source], "cal_BF16_logits":{"path":str(path),"sha256":sha(path)},
                    "buffer_hash":old.tensor_hash(buffers(model)), "precision_metric_columns":list(old.METRICS),
                    "FP32_to_BF16_metrics_per_sequence":precision.tolist(), "zero_L9_metrics_per_sequence":positive.tolist(),
                    "BF16_repeat_exact":True, "parameter_count":sum(p.numel() for p in model.parameters())}
                write(RESULT / "preflight.json",result)
                del model, p32, p16, zero, logits, again, original
                torch.cuda.empty_cache()
                old.emit("E150_native_preflight",source=source,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            result.update(status="complete", physical_gpu=physical, peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                          visible_device_uuid=str(torch.cuda.get_device_properties(0).uuid), asset_manifest_sha256=sha(RESULT/"asset_manifest.json"))
            write(RESULT / "preflight.json",result)
    finally:
        if lock is not None: lock.close()
    return {"status":result["status"]}


@torch.no_grad()
def evaluate(physical):
    plan, asset = ready(); pre = read(RESULT / "preflight.json")
    if pre["status"] != "complete" or pre["source_sha256"] != proof(): raise ValueError("Matching complete calibration preflight required")
    with np.load(plan["path"]) as raw:
        held, valid = raw["held"].copy(), raw["held_mask"].copy()
        cal, cal_valid = raw["cal"][:2,:129].copy(), raw["cal_mask"][:2,:128].copy()
    lock = None
    try:
        with Budget("mature_full_system_16_cells") as budget:
            lock = old.gpu_lock(physical)
            models = []
            for source in range(2):
                budget.check(); models.append(load_bf16(source))
                info = pre["models"][str(source)]; raw = info["cal_BF16_logits"]
                if sha(raw["path"]) != raw["sha256"] or old.tensor_hash(buffers(models[-1])) != info["buffer_hash"]:
                    raise ValueError("Canonical BF16 native buffers/cal artifact differ")
                with np.load(raw["path"]) as f: ref = torch.from_numpy(f["logits"].copy()).view(torch.bfloat16).to("cuda:0")
                ids = torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
                m = torch.cat((torch.ones((2,1),device="cuda:0",dtype=torch.bool),torch.from_numpy(cal_valid).to("cuda:0")),1)
                if not torch.equal(fwd(models[-1],ids[:,:-1],m[:,:-1]),ref): raise ValueError("Canonical native calibration reload differs")
                del ids,m,ref
            blocks = original_blocks(models)
            before = [old.tensor_hash(m.state_dict()) for m in models]
            before_buffers = [old.tensor_hash(buffers(m)) for m in models]
            counts = [0]*4
            for name,p in models[0].named_parameters(): counts[group_index(name,127)] += p.numel()
            if not all(counts): raise ValueError("Empty source factor")
            values = np.empty((16,64,512,2,4),np.float32)
            for start in range(0,64,4):
                budget.check(); restore(models,blocks)
                ids = torch.from_numpy(held[start:start+4].astype(np.int64)).to("cuda:0")
                mask = torch.cat((torch.ones((len(ids),1),device="cuda:0",dtype=torch.bool),torch.from_numpy(valid[start:start+4]).to("cuda:0")),1)
                refs = [fwd(m,ids[:,:-1],mask[:,:-1]) for m in models]
                logp = [r.float().log_softmax(-1) for r in refs]
                for index,case in enumerate(CASES):
                    budget.check(); model = assemble(models,blocks,case)
                    logits = fwd(model,ids[:,:-1],mask[:,:-1])
                    if len(set(case)) == 1 and not torch.equal(logits,refs[case[0]]): raise ValueError("Full native corner assembly differs")
                    q = logits.float().log_softmax(-1)
                    for ref in range(2): values[index,start:start+4,:,ref] = old.prediction_metrics(logp[ref],q,ids[:,1:]).cpu().numpy()
                    del q,logits
                del refs,logp,ids,mask
                old.emit("E150_cube_batch",sequences=start+4,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            restore(models,blocks)
            if any(old.tensor_hash(m.state_dict()) != h for m,h in zip(models,before)): raise ValueError("Source parameters mutated")
            if any(old.tensor_hash(buffers(m)) != h for m,h in zip(models,before_buffers)): raise ValueError("Source buffers mutated")
            if not np.array_equal(values[...,0,0],values[...,1,0]): raise ValueError("Reference-dependent NLL")
            path = RAW / "cube_metrics.npz"
            if path.exists(): raise ValueError("Refusing to replace full cube metrics")
            np.savez_compressed(path,metrics=values,valid=valid,cases=np.array(CASES),fields=np.array(old.METRICS))
            result = {"experiment":"E150", "status":"complete", "source_sha256":proof(), "input_plan_sha256":sha(RESULT/"plan.json"),
                "asset_manifest_sha256":sha(RESULT/"asset_manifest.json"), "source_order":list(NAMES), "factor_order":list(FACTORS),
                "factor_parameter_counts":dict(zip(FACTORS,counts)), "source_parameter_hashes":before, "source_buffer_hashes":before_buffers,
                "controls":{"all_16_parameter_sources_tiny_checked":True,"native_corners_exact_all_held":True,
                            "native_calibration_reload_exact":True,"source_parameters_and_buffers_unchanged":True,"NLL_reference_invariant":True},
                "raw":{"path":str(path),"sha256":sha(path),"size_bytes":path.stat().st_size}, "physical_gpu":physical,
                "visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),"peak_allocated_bytes":torch.cuda.max_memory_allocated(),
                "software":{"torch":torch.__version__,"transformers":transformers.__version__,"deterministic":torch.are_deterministic_algorithms_enabled()},
                "scope":"Published protocol-package endpoints with a declared common parent; actual BF16 whole-model cast, no new training or independent-seed inference."}
            write(RESULT/"manifest.json",result)
    finally:
        if lock is not None: lock.close()
    return {"status":"complete"}


def analyze():
    manifest = read(RESULT/"manifest.json"); plan = read(RESULT/"plan.json")
    if manifest["status"] != "complete" or manifest["source_sha256"] != proof(): raise ValueError("Sealed complete result required")
    raw = manifest["raw"]
    if sha(raw["path"]) != raw["sha256"]: raise ValueError("Cube raw differs")
    with np.load(raw["path"]) as f: a = np.stack([data.masked_mean(v.astype(float),f["valid"]) for v in f["metrics"]])
    stats = lambda x: input_stats(np.asarray(x),plan["selected"],150001)
    y = {case:a[i,:,0,0] for i,case in enumerate(CASES)}
    result = {"experiment":"E150","status":"complete","cases":{},"interactions":{},"primary":{},
              "scope":"Equal sequence means over real targets; input-file CIs, not training-seed populations or unique semantic mechanisms."}
    for i,case in enumerate(CASES):
        name = "".join("AB"[k] for k in case)
        result["cases"][name] = {"nll":stats(y[case]),"nll_minus_AAAA":stats(y[case]-y[(0,0,0,0)]),
            "nll_minus_BBBB":stats(y[case]-y[(1,1,1,1)]),
            **{f"{n}_to_variant_KL":stats(a[i,:,r,1]) for r,n in enumerate("AB")},
            **{f"variant_to_{n}_KL":stats(a[i,:,r,2]) for r,n in enumerate("AB")}}
    for order in (2,3,4):
        for axes in itertools.combinations(range(4),order):
            for fixed in itertools.product(range(2),repeat=4-order):
                key = "_x_".join(FACTORS[i] for i in axes)+"_background_"+"".join("AB"[i] for i in fixed)
                result["interactions"][key] = stats(interaction(y,axes,fixed))
    for axes,label in (((1,2),"router_x_routed"),((2,3),"routed_x_shared")):
        value = np.mean([interaction(y,axes,f) for f in itertools.product(range(2),repeat=2)],axis=0)
        result["primary"][label] = {"mean_interaction":stats(value),"mean_pairing_cost":stats(-value/2)}
    value = y[(1,1,1,1)]-y[(0,1,1,1)]-y[(1,0,0,0)]+y[(0,0,0,0)]
    result["primary"]["dense_x_complete_MoE"] = {"interaction":stats(value),"pairing_cost":stats(-value/2)}
    write(RESULT/"summary.json",result)
    return {"status":"complete","native_NLL":[result["cases"][x]["nll"]["point"] for x in ("AAAA","BBBB")],"primary":result["primary"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("self-test","preflight","evaluate","analyze")); p.add_argument("--physical-gpu",type=int,default=0)
    args = p.parse_args(); torch.set_num_threads(4)
    output = self_test() if args.mode == "self-test" else preflight(args.physical_gpu) if args.mode == "preflight" else evaluate(args.physical_gpu) if args.mode == "evaluate" else analyze()
    print(json.dumps(output,indent=2),flush=True)
