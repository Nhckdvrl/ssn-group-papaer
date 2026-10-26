"""CPU raw-array consistency audit; no model reruns or claim-level promotion."""
import hashlib
import json
from pathlib import Path
import numpy as np

WB = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as stream: return hashlib.file_digest(stream,"sha256").hexdigest()


def read(path): return json.loads(Path(path).read_text())


def main():
    grafts = read(WB/"results/e148/grafts.json"); summary = read(WB/"results/e148/summary.json")
    errors, raw_files = {}, {}
    for key, info in grafts["receivers"].items():
        path = info["raw"]["path"]; digest = sha(path)
        assert digest == info["raw"]["sha256"]
        raw_files[path] = digest
        with np.load(path) as f: names=f["names"].tolist(); a=f["metrics"].astype(float).mean(2)
        native = a[names.index("native"),:,0]
        record = read(WB/f"results/e148/{info['receiver']}.json")
        logged = np.array(next(r for r in record["evaluations"] if r["step"] == info["step"])["nll_rows"])
        errors[key+"_native_vs_saved_NLL"] = float(np.max(np.abs(native-logged)))
        for i,name in enumerate(names):
            errors[key+"_"+name+"_NLL_point"] = abs(float((a[i,:,0]-native).mean())-summary["grafts"][key][name]["delta_nll"]["point"])
    manifest = read(WB/"results/e149/manifest.json"); report = read(WB/"results/e149/summary.json")
    path=manifest["raw"]["path"]; digest=sha(path)
    assert digest == manifest["raw"]["sha256"];raw_files[path]=digest
    with np.load(path) as f:
        values=f["metrics"].astype(float); cases=f["cases"]
    assert values.shape == (8,64,512,2,4)
    assert np.array_equal(values[...,0,0],values[...,1,0])
    rows=values.mean(2)
    for i,case in enumerate(cases):
        name="".join("AB"[int(v)] for v in case)
        errors[name+"_cube_NLL_point"] = abs(float(rows[i,:,0,0].mean())-report["cases"][name]["nll"]["point"])
    errors["cube_vs_E148_A_B_KL"] = abs(float(rows[-1,:,0,1].mean())-summary["pairs"]["A_672_to_B_672"]["forward_kl"]["point"])
    pairing=(rows[3,:,0,0]+rows[4,:,0,0]-rows[0,:,0,0]-rows[7,:,0,0])/2
    errors["cube_pairing_cost_algebra"] = abs(float(pairing.mean())+report["interactions"]["backbone_x_complete_MoE"]["point"]/2)
    if max(errors.values()) > 1e-10: raise ArithmeticError(errors)
    archive=read(WB/"results/e148/archive.json")
    assert archive["verified_files"] == len(archive["files"]) == 72
    for info in archive["files"].values():
        path=Path(info["path"])
        assert path.stat().st_size == info["size_bytes"] and path.stat().st_mtime_ns == info["destination_mtime_ns"]
    result={"status":"passed","CPU_only":True,"audit_source_sha256":sha(__file__),"raw_sha256":raw_files,
            "point_absolute_errors":errors,"max_absolute_error":max(errors.values()),
            "durable_archive_files":72,"durable_archive_bytes":archive["verified_bytes"],
            "archive_manifest_sha256":sha(WB/"results/e148/archive.json"),
            "scope":"Same researcher, raw-array/hash/algebra consistency; archive SHA was verified during copying, this pass checks stat identity. Not an independent L3 audit or new evidence population."}
    (WB/"results/e148149_raw_verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":"passed","max_absolute_error":max(errors.values()),"durable_files":72},indent=2))


if __name__ == "__main__": main()
