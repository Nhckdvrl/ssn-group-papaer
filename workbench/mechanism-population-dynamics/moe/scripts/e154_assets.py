"""E154 pinned public parent retrieval; no torch/model-code execution."""
import argparse
import datetime
import json
import re
from pathlib import Path
import e150_prepare_assets as a

RESULT=a.WB/"results/e154"
NAME="StdMoE_1b14b_1T_Preanneal"


def main(mode):
    assert (a.WB/"experiments/E154-native-parent-formation-boundary.md").exists()
    pin=json.loads(a.PINS.read_text())[NAME]
    small=[f["rfilename"] for f in pin["files"] if f["rfilename"].endswith((".json",".py",".txt",".model",".jinja"))]
    weights=[f["rfilename"] for f in pin["files"] if f["rfilename"].endswith(".safetensors")]
    requested=small if mode=="metadata" else small+weights
    result={"experiment":"E154","status":"partial","asset_fetch_source_sha256":a.sha(__file__),
            "shared_asset_helpers_sha256":a.sha(a.__file__),"public_metadata_sha256":a.sha(a.PINS),
            "cache":str(a.CACHE),"model_code_executed":False,"training_or_inference_performed":False}
    directory=Path(a.snapshot_download(pin["id"],revision=pin["sha"],allow_patterns=requested,cache_dir=str(a.CACHE),max_workers=2,token=False))
    files={}
    for remote in pin["files"]:
        name=remote["rfilename"]
        if name not in requested:
            continue
        path=directory/name
        actual=a.sha(path)
        expected=remote.get("lfs",{}).get("sha256")
        if path.stat().st_size!=remote["size"] or (expected and actual!=expected):
            raise ValueError("Pinned public parent size/LFS mismatch")
        if not expected:
            import hashlib
            data=path.read_bytes()
            blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            if blob!=remote["blobId"]:
                raise ValueError("Pinned public parent Git blob mismatch")
        files[name]={"path":str(path),"sha256":actual,"size_bytes":path.stat().st_size,
                     "public_lfs_sha256":expected,"public_blob_id":remote["blobId"]}
        print(json.dumps({"event":"E154_asset_verified","file":name,"size_bytes":path.stat().st_size}),flush=True)
    result.update(status="metadata_complete" if mode=="metadata" else "complete",
                  verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  model={"repo_id":pin["id"],"revision":pin["sha"],"path":str(directory),"files":files})
    a.write(RESULT/("metadata.json" if mode=="metadata" else "asset_manifest.json"),result)
    print(json.dumps({"status":result["status"],"files":len(files)}),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("metadata","weights"))
    args=p.parse_args()
    try:
        main(args.mode)
    except Exception as error:
        message=re.sub(r"https?://\S+","<URL omitted>",str(error))[:400]
        a.write(RESULT/f"{args.mode}_failure.json",{"status":"failed","type":type(error).__name__,"message":message})
        raise SystemExit(f"E154 retrieval failed ({type(error).__name__}); see recorded failure.")
