#!/usr/bin/env python3
"""One-shot E128 endpoint watcher, E127 fidelity scoring, and asset archive."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, time
from pathlib import Path
WB = Path(__file__).resolve().parents[1]
OUT = Path("/tmp/xiang-moe-20261025/e128_seed0")
EVAL = WB / "results/e128/predictive_fidelity.json"
FINAL = WB / "results/e128/finalization.json"
ARCHIVE = Path.home() / "mechpop_cache/e128_seed0_512m"
DRIVER, EVALUATOR = WB/"scripts/e128_epoch_recovery.py", WB/"scripts/e127_predictive_fidelity.py"
STEPS, TOKENS = 62500, 512_000_000
def read(p):
    try: return json.loads(Path(p).read_text())
    except (FileNotFoundError, json.JSONDecodeError): return None
def write(p, x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".partial")
    t.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+"\n"); t.replace(p)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(8<<20),b""): h.update(b)
    return h.hexdigest()
def cmdline(pid):
    try: return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0",b" ").decode(errors="replace").strip()
    except FileNotFoundError: return None
def process_exited(command): return not bool(command)
def gpu2_status():
    try:
        row=subprocess.check_output(["nvidia-smi","-i","2","--query-gpu=memory.used,utilization.gpu","--format=csv,noheader"],text=True).strip()
        mem,util=[x.strip() for x in row.split(",")]
        return {"physical_gpu":2,"memory_used_mib":int(mem.split()[0]),"utilization_percent":int(util.split()[0])}
    except Exception as e: return {"physical_gpu":2,"query_error":f"{type(e).__name__}: {e}"}
def gpu2_free(state): return "query_error" not in state and state["memory_used_mib"]<1024 and state["utilization_percent"]<=5
def ready(s,f): return f is None and s is not None and s.get("status")=="complete" and s.get("step")==STEPS and s.get("planned_steps")==STEPS and s.get("train_tokens")==TOKENS
def scoped_guard(old,step,expected,reference,registered):
    if expected==STEPS:
        if not registered or reference or step!=STEPS: raise ValueError("62500 allowed only for validated E128")
        return
    return old(step,expected,reference)
def self_test():
    from e127_predictive_fidelity import guard_step
    for a in ((STEPS,STEPS,False,True),(3906,3906,True,True),(15625,15625,False,True)): scoped_guard(guard_step,*a)
    for a in ((STEPS,STEPS,False,False),(STEPS,STEPS,True,True),(15625,STEPS,False,True),(3906,3906,False,True)):
        try: scoped_guard(guard_step,*a)
        except ValueError: continue
        raise AssertionError(f"guard accepted {a}")
    calls=[]; incomplete={"status":"running","step":10,"planned_steps":STEPS,"train_tokens":81920}
    if ready(incomplete,None): calls.append("evaluate")
    assert not calls and not ready({"status":"complete","step":STEPS,"planned_steps":STEPS,"train_tokens":TOKENS},{"x":1})
    assert process_exited(None) and process_exited("") and not process_exited("python e128_epoch_recovery.py")
    assert gpu2_free({"memory_used_mib":18,"utilization_percent":0})
    assert not gpu2_free({"memory_used_mib":1024,"utilization_percent":0})
    assert not gpu2_free({"memory_used_mib":18,"utilization_percent":6})
    print("E128 finalizer CPU checks passed: scoped guard; incomplete endpoint does not evaluate.")
def validate(out):
    s,p,d=(read(out/n) for n in ("training_summary.json","provenance.json","driver_protocol.json"))
    if not ready(s,read(out/"failure.json")): raise ValueError("E128 training endpoint is incomplete")
    a=p["args"]; want={"seed":0,"order_seed":0,"layer":9,"experts":64,"expert_size":1024,"top_k":8,
        "steps":STEPS,"seq_len":512,"batch_size":16,"accum":1,"max_train_tokens":TOKENS,"replacement":"moe","dtype":"bfloat16","max_hours":8.}
    if any(a.get(k)!=v for k,v in want.items()): raise ValueError("Provenance does not match registered E128")
    dh=sha(DRIVER)
    if d.get("experiment")!="E128" or d.get("cpu_test") is not False or d.get("driver_sha256")!=dh or a.get("driver_sha256")!=dh:
        raise ValueError("E128 driver protocol/hash mismatch")
    if s.get("config_hash")!=p.get("config_hash") or s.get("frozen_sample_hash_before")!=s.get("frozen_sample_hash_after") or s.get("frozen_sample_hash_after")!=p.get("frozen_sample_hash"):
        raise ValueError("Summary/provenance/frozen hash mismatch")
    cp=out/"checkpoint.pt"
    if not cp.is_file(): raise FileNotFoundError(cp)
    import torch; x=torch.load(cp,map_location="cpu",mmap=True,weights_only=False)
    if x.get("step")!=STEPS or x.get("config_hash")!=s["config_hash"] or x.get("frozen_sample_hash")!=p["frozen_sample_hash"]:
        raise ValueError("Checkpoint metadata differs from E128 endpoint")
    return s,p,d,cp,dh
def evaluate(cp,dh,path):
    import argparse as ap
    import e127_predictive_fidelity as e127
    old=e127.guard_step
    e127.guard_step=lambda step,expected,reference: scoped_guard(old,step,expected,reference,True)
    a=ap.Namespace(checkpoint=str(cp),model=None,data=None,device="cuda:0",output=str(path),
                   expected_step=STEPS,reference_calibration=False,bootstrap=1000)
    r=e127.evaluate(a); eh=sha(EVALUATOR)
    r.update({"experiment":"E128","e128_driver_sha256":dh,"e127_evaluator_sha256":eh,
              "guard_scope":"Process-local E128 step62500 only; original E127 guard retained otherwise"})
    write(path,r); return r,eh
def archive(out,cp,cpsha):
    names=("provenance.json","driver_protocol.json","gradient_audit.json","training_summary.json")
    if ARCHIVE.exists():
        m=read(ARCHIVE/"archive_manifest.json")
        if m and m.get("checkpoint_sha256")==cpsha: return m
        raise FileExistsError(ARCHIVE)
    part=ARCHIVE.with_name(ARCHIVE.name+".partial")
    if part.exists(): raise FileExistsError(part)
    part.parent.mkdir(parents=True,exist_ok=True); part.mkdir()
    files={}
    for n in ("checkpoint.pt",)+names:
        src=cp if n=="checkpoint.pt" else out/n; dst=part/n; shutil.copy2(src,dst)
        files[n]={"size_bytes":dst.stat().st_size,"sha256":sha(dst)}
    if files["checkpoint.pt"]["sha256"]!=cpsha: raise IOError("Archived checkpoint SHA mismatch")
    (part/"checkpoint.sha256").write_text(cpsha+"  checkpoint.pt\n")
    m={"experiment":"E128","checkpoint_sha256":cpsha,"files":files}; write(part/"archive_manifest.json",m)
    part.rename(ARCHIVE); return m
def finish(out,eval_path,final_path):
    gpu=gpu2_status(); s,p,d,cp,dh=validate(out); cpsha=sha(cp); ev=None; err=None
    if not gpu2_free(gpu):
        try: am=archive(out,cp,cpsha)
        except Exception as e:
            write(final_path,{"status":"archive_failed_gpu2_busy","experiment":"E128","error":f"{type(e).__name__}: {e}","gpu2_preflight":gpu,"checkpoint_sha256":cpsha}); return
        write(final_path,{"status":"evaluation_deferred_gpu_busy","experiment":"E128","step":STEPS,
            "train_tokens":TOKENS,"gpu2_preflight":gpu,"evaluation":None,"checkpoint_sha256":cpsha,
            "archive":str(ARCHIVE),"archived_checkpoint_sha256":am["checkpoint_sha256"]}); return
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="2": raise RuntimeError("Set CUDA_VISIBLE_DEVICES=2 for E127 scoring")
    import torch
    if not torch.cuda.is_available() or torch.cuda.device_count()!=1: raise RuntimeError("Expected only GPU2 visible")
    try: ev,eh=evaluate(cp,dh,eval_path)
    except Exception as e: err=f"{type(e).__name__}: {e}"
    try: am=archive(out,cp,cpsha)
    except Exception as e:
        write(final_path,{"status":"archive_failed","experiment":"E128","error":f"{type(e).__name__}: {e}",
                          "evaluation_error":err,"gpu2_preflight":gpu,"checkpoint_sha256":cpsha,"evaluation":str(eval_path)})
        return
    status="complete" if err is None else "evaluation_failed"
    write(final_path,{"status":status,"experiment":"E128","step":STEPS,"train_tokens":TOKENS,
        "driver_sha256":dh,"e127_evaluator_sha256":sha(EVALUATOR),"evaluation_error":err,
        "gpu2_preflight":gpu,
        "predictive_fidelity":str(eval_path) if ev else None,"predictive_fidelity_sha256":sha(eval_path) if ev else None,
        "checkpoint_sha256":cpsha,"archive":str(ARCHIVE),"archived_checkpoint_sha256":am["checkpoint_sha256"],
        "evaluation_scope":"E127 dense-teacher KL on original held windows; one seed"})
def watch(a):
    deadline=time.monotonic()+a.max_watch_hours*3600; out=a.output_dir
    print(json.dumps({"watching_pid":a.pid,"poll_seconds":a.poll_seconds,"max_watch_hours":a.max_watch_hours}),flush=True)
    while time.monotonic()<deadline:
        s,f=read(out/"training_summary.json"),read(out/"failure.json"); c=cmdline(a.pid)
        if c and ("e128_epoch_recovery.py" not in c or "--mode train" not in c or str(out) not in c):
            write(a.finalization,{"status":"pid_command_mismatch","pid":a.pid,"evaluation":None}); return
        if f: write(a.finalization,{"status":"training_failed","pid":a.pid,"failure":f,"training_summary":s,"evaluation":None}); return
        if s and s.get("status")=="complete":
            if not ready(s,f): write(a.finalization,{"status":"invalid_endpoint","pid":a.pid,"training_summary":s,"evaluation":None}); return
            if process_exited(c): finish(out,a.evaluation,a.finalization); return
        elif process_exited(c):
            write(a.finalization,{"status":"training_exited_incomplete","pid":a.pid,"training_summary":s,"failure":f,"evaluation":None}); return
        time.sleep(a.poll_seconds)
    write(a.finalization,{"status":"watch_timeout_no_evaluation","pid":a.pid,"training_summary":read(out/"training_summary.json"),"failure":read(out/"failure.json"),"evaluation":None})
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--watch",action="store_true"); p.add_argument("--self-test",action="store_true")
    p.add_argument("--pid",type=int,default=3801880); p.add_argument("--poll-seconds",type=int,default=30); p.add_argument("--max-watch-hours",type=float,default=9.)
    p.add_argument("--output-dir",type=Path,default=OUT); p.add_argument("--evaluation",type=Path,default=EVAL)
    p.add_argument("--finalization",type=Path,default=FINAL); args=p.parse_args()
    if args.self_test: self_test(); return
    if not args.watch or args.poll_seconds<1 or args.max_watch_hours<=0: p.error("Use --watch with a positive poll interval and watch budget")
    watch(args)
if __name__=="__main__": main()
