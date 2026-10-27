"""Read-only sampled weight-lineage sanity check; not a training-state chain."""
import hashlib
import json
from pathlib import Path
import numpy as np
from safetensors import safe_open
import e154_assets as a

RESULT=a.RESULT


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def main():
    parent=json.loads((RESULT/"asset_manifest.json").read_text())
    descendants=json.loads((a.WB/"results/e150/asset_manifest.json").read_text())
    assert parent["status"]==descendants["status"]=="complete"
    records={"P":parent["model"],"A":descendants["models"]["StdMoE_1b14b_1T"],
             "B":descendants["models"]["StdMoE_1b14b_1T_EmoAnnealed"]}
    indices={label:json.loads((Path(record["path"])/"model.safetensors.index.json").read_text())["weight_map"]
             for label,record in records.items()}
    names=[f"model.layers.{layer}.{suffix}" for layer in (0,8,15) for suffix in
           ("self_attn.q_proj.weight","mlp.gate.weight","mlp.experts.0.gate_proj.weight","mlp.experts.127.down_proj.weight")]
    out={}
    for name in names:
        tensors={}
        for label,record in records.items():
            with safe_open(Path(record["path"])/indices[label][name],framework="np") as f:
                tensors[label]=f.get_tensor(name).astype(np.float64)
        base=tensors["P"].ravel()
        row={}
        for label in ("A","B"):
            value=tensors[label].ravel()
            assert value.shape==base.shape and np.isfinite(value).all()
            delta=value-base
            row[label]={"cosine_to_parent":float(np.dot(value,base)/(np.linalg.norm(value)*np.linalg.norm(base))),
                        "relative_L2_to_parent":float(np.linalg.norm(delta)/np.linalg.norm(base)),
                        "all_equal_parent":bool(np.array_equal(value,base))}
        out[name]=row
    result={"experiment":"E154","status":"complete","sampled_layers":[0,8,15],"sampled_parameters":len(names),
            "source_sha256":sha(__file__),"parent_asset_manifest_sha256":sha(RESULT/"asset_manifest.json"),
            "descendant_asset_manifest_sha256":sha(a.WB/"results/e150/asset_manifest.json"),"comparisons":out,
            "scope":"Sampled published-weight proximity only. Cannot prove exact common starting parameters, optimizer, batches or causal protocol isolation."}
    (RESULT/"weight_provenance.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":"complete","sampled_parameters":len(names),
                     "minimum_cosine":{label:min(v[label]["cosine_to_parent"] for v in out.values()) for label in ("A","B")}},indent=2))


if __name__=="__main__":
    main()
