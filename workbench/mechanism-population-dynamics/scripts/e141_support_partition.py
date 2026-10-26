"""E141: native on-support contribution partition; immutable descriptor-bound replay.

No training, rematching, off-support expert calls, or full language model load.
Descriptors bind each group to an existing complete readout, final checkpoints,
calibration maps and original per-sequence component statistics.
"""
from __future__ import annotations
import argparse, fcntl, itertools, json, socket, tempfile, time
from pathlib import Path
import numpy as np
import torch
import transformers
import e137_components as native

c, assets, WB = native.c, native.assets, native.WB
STUDENTS = ("seed0", "seed1", "seed2")
PAIRS = tuple(itertools.combinations(range(3), 2))
GROUPS = ("free", "fixed", "warm")
CACHE_SHA = "2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43"
NATIVE_SHA = "86c57c0bc40c14d7778c036e92380e97ef3a071feeba4be484b2b45cc39bee63"
FIELDS = ("left_on_count", "right_on_count", "both_on_count", "xor_count", "neither_on_count",
          "left_component_energy", "right_component_energy", "total_SSE", "xor_SSE", "both_SSE",
          "both_f_left_energy", "both_f_right_energy", "both_f_SSE", "both_f_dot",
          "both_w_left_sum", "both_w_right_sum", "both_w_left_squared", "both_w_right_squared", "both_w_delta_squared",
          "ideal_product_delta_SSE", "gate_term_SSE", "content_term_SSE", "gate_content_cross",
          "decomposition_residual_SSE", "product_floor_delta_SSE", "ideal_floor_cross",
          "left_product_floor_SSE", "right_product_floor_SSE", "actual_ideal_floor_scalar_residual")
I = {name: i for i, name in enumerate(FIELDS)}
MAIN = ("cohort_total_per_position", "cohort_xor_per_position", "cohort_both_per_position")


class Budget(c.Budget):
    def __init__(self, path, phase): super().__init__(path, phase, limit=900.)
    def update(self, operation):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            state = assets.read(self.path) or {"experiment": "E141", "host": socket.gethostname(), "completed_seconds": 0., "active": {}, "runs": []}
            if state.get("experiment") != "E141" or state["host"] != socket.gethostname(): raise ValueError("Separate E141 node-local additive ledger required")
            return self.finish_update(state, operation)
    def finish_update(self, state, operation):
        result = operation(state); assets.write(self.path, state); return result
    def check(self):
        used = self.update(lambda s: s["completed_seconds"] + sum(time.monotonic() - r["started"] for r in s["active"].values()))
        if used >= 900: raise TimeoutError("E141 aggregate900GPU-second budget exhausted; no score-based stopping")
        return used


def at(value, path):
    for key in path: value = value[key]
    return value


def preflight(args):
    if assets.sha(Path(native.__file__)) != NATIVE_SHA or transformers.__version__ != "4.57.6": raise ValueError("Frozen native trace/HF version differs")
    c.source_proof()
    if assets.sha(args.cache_root / "manifest.json") != CACHE_SHA: raise ValueError("Immutable original cache manifest required")
    manifest = c.cache_manifest(args.cache_root)
    if torch.__version__ != manifest["prepare_proof"]["assets"]["torch"]: raise ValueError("Original native-forward Torch version required")
    hp = args.cache_root / "held_H.npy"
    if assets.sha(hp) != manifest["files"][hp.name]["sha256"]: raise ValueError("Held native H bytes differ")
    hidden = np.load(hp, mmap_mode="r", allow_pickle=False)
    if hidden.shape != (32, 16, 512, 2048) or hidden.dtype != np.uint16: raise ValueError("Exact original BF16-bit held H layout required")
    descriptors = {}
    for path in args.descriptor:
        doc = assets.read(path)
        if doc.get("schema") != "E141-group-descriptors-v1": raise ValueError("Unknown descriptor schema")
        for name, desc in doc["groups"].items():
            if name not in GROUPS or (name in descriptors and descriptors[name] != desc): raise ValueError("Unknown/conflicting group descriptor")
            descriptors[name] = desc
    result = {}; common_rows = None
    for group in args.groups:
        desc = descriptors[group]; source = assets.read(desc["readout"])
        if assets.sha(desc["readout"]) != desc["readout_sha256"] or source.get("status") != "complete" or source.get("errors"):
            raise ValueError("Descriptor requires immutable complete original readout")
        if source["cache_manifest_sha256"] != CACHE_SHA: raise ValueError("Original readout uses another cache")
        cal = at(source, desc["calibration_path"]); record = at(source, desc["components_path"])
        if assets.sha(cal["cost_path"]) != cal["cost_sha256"]: raise ValueError("Original calibration cost SHA differs")
        if cal["Hcal_sha256"] != manifest["prepare_proof"]["assets"]["assets"]["public_native_Hcal.npy"]["sha256"]:
            raise ValueError("Original training-only Hcal identity differs")
        maps = {"seed1": list(range(64)), **{n: cal["maps"][n]["source_to_seed1"] for n in ("seed0", "seed2")}}
        if maps != desc["maps_source_to_seed1"] or any(sorted(m) != list(range(64)) for m in maps.values()): raise ValueError("Locked bijective maps differ")
        for key in ("raw", "metadata"):
            if assets.sha(record[key]) != record[key + "_sha256"]: raise ValueError("Original component source bytes differ")
        metadata = assets.read(record["metadata"])
        if metadata["maps_source_to_seed1"] != maps or len(metadata["rows"]) != 512: raise ValueError("Original row/map identity differs")
        rows = metadata["rows"]
        if common_rows is not None and rows != common_rows: raise ValueError("Groups do not use the same held sequences/order")
        common_rows = rows
        states = {}; proof = {}
        for name in STUDENTS:
            spec = desc["students"][name]; old = at(source, spec["proof_path"]); path = Path(spec["checkpoint"])
            if spec["checkpoint_sha256"] != old["checkpoint_sha256"] or assets.sha(path) != spec["checkpoint_sha256"]:
                raise ValueError("Original complete checkpoint file SHA differs")
            cp = torch.load(path, map_location="cpu", mmap=True, weights_only=False); state = cp[spec["state_key"]]
            digest = c.tensor_state_hash(state)
            if (cp.get("schema"), cp.get("experiment"), cp.get("step")) != (spec["schema"], spec["experiment"], 4096): raise ValueError("Wrong registered final CP identity")
            if cp.get("cache_manifest_sha256") != CACHE_SHA or not np.array_equal(cp["cache_batch_counts"], np.full(1024, 4)):
                raise ValueError("Wrong cache/exposure endpoint")
            if digest != spec["full_tensor_sha256"] or digest != old.get("full_tensor_sha256", old.get("tensor_sha256")) or any(t.dtype != torch.float32 for t in state.values()):
                raise ValueError("FP32 source bank tensor identity differs")
            states[name] = state; proof[name] = {"checkpoint_sha256": spec["checkpoint_sha256"], "full_tensor_sha256": digest}
        if desc.get("known_common_gate") and any(not torch.equal(states[n]["block.gate.weight"], states["seed1"]["block.gate.weight"]) for n in STUDENTS):
            raise ValueError("Descriptor's known common-gate control differs")
        result[group] = {"descriptor": desc, "descriptor_sha256": c.base.digest_json(desc), "states": states, "proofs": proof,
                         "maps": maps, "reference": record, "reference_metadata": metadata}
    return manifest, hidden, result


def row_with_weight(trace, original):
    row = trace["experts"][original]; qi = row["query"]
    hits = trace["selected"][qi] == original
    if not torch.all(hits.sum(-1) == 1): raise RuntimeError("Native selected query does not uniquely contain its expert")
    slot = hits.long().argmax(-1)
    return {**row, "w": trace["weights"][qi].gather(1, slot[:, None])[:, 0]}


def pair_statistics(left, right, count, sequence, batch):
    """Only actual native-selected rows contain f; no expert is queried here."""
    device = sequence.device; values = torch.zeros((count, len(FIELDS)), dtype=torch.float64, device=device)
    il = torch.full((count,), -1, dtype=torch.long, device=device); ir = il.clone()
    ql, qr = left["query"], right["query"]; il[ql] = torch.arange(len(ql), device=device); ir[qr] = torch.arange(len(qr), device=device)
    both = (il >= 0) & (ir >= 0); xor = (il >= 0) ^ (ir >= 0); qi = both.nonzero().flatten()
    values[ql, I["left_on_count"]] = 1; values[qr, I["right_on_count"]] = 1
    values[:, I["both_on_count"]] = both.double(); values[:, I["xor_count"]] = xor.double(); values[:, I["neither_on_count"]] = ((il < 0) & (ir < 0)).double()
    el, er = native.norm2(left["component"]), native.norm2(right["component"])
    values[ql, I["left_component_energy"]] = el; values[qr, I["right_component_energy"]] = er
    values[ql, I["total_SSE"]] += el; values[qr, I["total_SSE"]] += er
    fl, fr = left["f"][il[qi]].double(), right["f"][ir[qi]].double()
    wl, wr = left["w"][il[qi]].double()[:, None], right["w"][ir[qi]].double()[:, None]
    cl, cr = left["component"][il[qi]].double(), right["component"][ir[qi]].double()
    actual = cl - cr; ideal = wl * fl - wr * fr
    gate = (wl - wr) * (fl + fr) / 2; content = (wl + wr) * (fl - fr) / 2
    floor_l, floor_r = cl - wl * fl, cr - wr * fr; floor = floor_l - floor_r
    sq = lambda v: v.square().sum(-1)
    data = {"both_SSE": sq(actual), "both_f_left_energy": sq(fl), "both_f_right_energy": sq(fr), "both_f_SSE": sq(fl - fr), "both_f_dot": (fl * fr).sum(-1),
            "both_w_left_sum": wl[:, 0], "both_w_right_sum": wr[:, 0], "both_w_left_squared": wl[:, 0].square(), "both_w_right_squared": wr[:, 0].square(),
            "both_w_delta_squared": (wl[:, 0] - wr[:, 0]).square(), "ideal_product_delta_SSE": sq(ideal), "gate_term_SSE": sq(gate), "content_term_SSE": sq(content),
            "gate_content_cross": 2 * (gate * content).sum(-1), "decomposition_residual_SSE": sq(ideal - gate - content),
            "product_floor_delta_SSE": sq(floor), "ideal_floor_cross": 2 * (ideal * floor).sum(-1),
            "left_product_floor_SSE": sq(floor_l), "right_product_floor_SSE": sq(floor_r),
            "actual_ideal_floor_scalar_residual": sq(actual) - sq(ideal) - sq(floor) - 2 * (ideal * floor).sum(-1)}
    values[qi, I["total_SSE"]] = data["both_SSE"]
    values[xor, I["xor_SSE"]] = values[xor, I["total_SSE"]]
    for name, value in data.items(): values[qi, I[name]] = value
    output = torch.zeros((batch, len(FIELDS)), dtype=torch.float64, device=device)
    return output.index_add_(0, sequence, values)


@torch.no_grad()
def measure(blocks, hidden, maps, budget):
    n = hidden.shape[0] * hidden.shape[1]; query = torch.arange(n, device=hidden.device)
    sequence = torch.arange(hidden.shape[0], device=hidden.device).repeat_interleave(hidden.shape[1]); traces = {}
    for name in STUDENTS:
        budget.check()
        with torch.autocast(hidden.device.type, dtype=torch.bfloat16): traces[name] = native.native_trace(blocks[name].block, hidden, query)
    output = torch.zeros((hidden.shape[0], 64, 3, len(FIELDS)), dtype=torch.float64, device=hidden.device)
    inverse = {name: np.argsort(maps[name]) for name in STUDENTS}
    for e in range(64):
        if e % 8 == 0: budget.check()
        rows = [row_with_weight(traces[name], int(inverse[name][e])) for name in STUDENTS]
        for p, (l, r) in enumerate(PAIRS): output[:, e, p] = pair_statistics(rows[l], rows[r], n, sequence, hidden.shape[0])
    return output.cpu().numpy()


def pair_numbers(row, positions):
    d = dict(zip(FIELDS, row)); both = d["both_on_count"]
    result = {name + "_per_position": float(value / positions) for name, value in d.items()}
    result["both_f_SSE_per_common_on"] = float(d["both_f_SSE"] / both) if both else None
    energy = d["both_f_left_energy"] * d["both_f_right_energy"]
    result["both_f_pooled_cosine"] = float(d["both_f_dot"] / np.sqrt(energy)) if energy > 0 else None
    for name in ("both_w_left_sum", "both_w_right_sum", "both_w_delta_squared"):
        result[name + "_per_common_on"] = float(d[name] / both) if both else None
    return result


def numbers(totals, positions):
    result = {"cohort_" + k + "_per_position": float(totals[:, I[field]].sum() / (9 * positions))
              for k, field in (("total", "total_SSE"), ("xor", "xor_SSE"), ("both", "both_SSE"))}
    for p, (l, r) in enumerate(PAIRS):
        for key, value in pair_numbers(totals[p], positions).items(): result[f"seed{l}_seed{r}/" + key] = value
    return result


def draws_for(raw, rows):
    labels = list(dict.fromkeys((r["source"], r["file_id"]) for r in rows))
    groups = [np.array([i for i, r in enumerate(rows) if (r["source"], r["file_id"]) == label]) for label in labels]
    if len(rows) != 512 or len(groups) != 32: raise ValueError("Original512 sequences/32 held file clusters required")
    grouped = np.stack([raw[g].sum((0, 1)) for g in groups]); positions = np.array([len(g) * 512 for g in groups])
    draws = np.random.default_rng(141).integers(0, len(groups), (1000, len(groups)))
    return [numbers(grouped.sum(0), positions.sum())] + [numbers(grouped[d].sum(0), positions[d].sum()) for d in draws]


def summarize(raw, rows):
    values = draws_for(raw, rows); point = values[0]; global_stats = {}
    for key, value in point.items():
        samples = [v[key] for v in values[1:] if v[key] is not None and np.isfinite(v[key])]
        global_stats[key] = {"point": value, "ci95": np.quantile(samples, [.025, .975]).tolist() if value is not None and len(samples) == 1000 else None, "defined_draws": len(samples)}
    table = [{"seed1_coordinate": e, "pairs": {f"seed{l}_seed{r}": {"raw_totals": dict(zip(FIELDS, raw[:, e, p].sum(0).tolist())),
              "statistics": pair_numbers(raw[:, e, p].sum(0), 262144)} for p, (l, r) in enumerate(PAIRS)}} for e in range(64)]
    return {"global": global_stats, "per_expert": table, "bootstrap_seed": 141, "bootstrap_iterations": 1000,
            "scope": "Input file-cluster CI, fixed observed cohort/maps. Pooled cosine is dot of concatenated common-on f vectors divided by pooled energies; zero energy undefined."}


def contrasts(records):
    result = {}
    for left, right in (("free", "fixed"), ("warm", "fixed"), ("warm", "free")):
        if left not in records or right not in records: continue
        values = []
        for group in (left, right):
            entry = records[group]
            if assets.sha(entry["raw"]) != entry["raw_sha256"] or assets.sha(entry["metadata"]) != entry["metadata_sha256"]: raise ValueError("Existing E141 raw mutated")
            rows = assets.read(entry["metadata"])["rows"]
            if values and rows != previous_rows: raise ValueError("Paired contrast row identity differs")
            with np.load(entry["raw"], allow_pickle=False) as data: values.append(draws_for(data["statistics"], rows))
            previous_rows = rows
        result[left + "_minus_" + right] = {key: {"point": values[0][0][key] - values[1][0][key],
            "paired_file_ci95": np.quantile([a[key] - b[key] for a, b in zip(values[0][1:], values[1][1:])], [.025, .975]).tolist()} for key in MAIN}
    return result


def reference_check(raw, group):
    with np.load(group["reference"]["raw"], allow_pickle=False) as source: old = source["expert"]
    fields = group["reference_metadata"]["expert_fields"]
    diffs = {f"seed{l}_seed{r}": float(np.max(np.abs(raw[:, :, p, I["total_SSE"]] - old[:, :, fields.index(f"pair_seed{l}_seed{r}_SSE")]))) for p, (l, r) in enumerate(PAIRS)}
    variance = raw[:, :, :, I["total_SSE"]].sum(-1) / 9
    # Same weights, hidden bytes and native B16 program: only F64 reductions differ.
    rtol, atol = 1e-10, 1e-9
    for p, (l, r) in enumerate(PAIRS):
        if not np.allclose(raw[:, :, p, I["total_SSE"]], old[:, :, fields.index(f"pair_seed{l}_seed{r}_SSE")], rtol=rtol, atol=atol):
            raise ArithmeticError(f"Native replay/reference pair SSE differs beyond F64 reduction tolerance: {diffs}")
    if not np.allclose(variance, old[:, :, fields.index("cohort_variance")], rtol=rtol, atol=atol): raise ArithmeticError("Native replay/reference cohort variance differs")
    if group["descriptor"].get("known_common_gate") and all(m == list(range(64)) for m in group["maps"].values()) and np.any(raw[..., I["xor_count"]] != 0):
        raise ArithmeticError("Known identical native gate/identity-map control has nonzero XOR")
    return {"pair_SSE_max_abs_difference": diffs, "cohort_variance_max_abs_difference": float(np.max(np.abs(variance - old[:, :, fields.index("cohort_variance")]))),
            "partition_max_abs_residual": float(np.max(np.abs(raw[..., I["total_SSE"]] - raw[..., I["xor_SSE"]] - raw[..., I["both_SSE"]]))),
            "F64_reduction_identity_rtol_atol": [rtol, atol],
            "scope": "Instrument same-program closure only; no scientific performance/role cutoff. A failure preserves raw and stops for investigation."}


def run(args):
    manifest, hidden, groups = preflight(args); args.raw_output.mkdir(parents=True, exist_ok=True)
    signature = assets.sha(__file__); result = assets.read(args.summary) or {"experiment": "E141", "script_sha256": signature,
        "native_trace_sha256": NATIVE_SHA, "cache_manifest_sha256": CACHE_SHA, "expected_groups": list(GROUPS), "groups": {}, "errors": {}, "failures": []}
    if (result["experiment"], result["script_sha256"], result["cache_manifest_sha256"]) != ("E141", signature, CACHE_SHA): raise ValueError("Cannot reuse result from another source/protocol")
    for name, group in groups.items():
        if name in result["groups"] and result["groups"][name]["descriptor_sha256"] != group["descriptor_sha256"]: raise ValueError("Existing immutable group descriptor differs")
    pending = [n for n in args.groups if n not in result["groups"]]
    if pending:
        gpu = c.select_gpu(args.physical_gpu); result["gpu_preflight"] = gpu
        with Budget(args.budget_file, "replay_" + "_".join(pending)) as budget:
            for name in pending:
                group = groups[name]; path = args.raw_output / f"{name}_partition.npz"; mp = path.with_suffix(".json")
                if path.exists() or mp.exists(): raise FileExistsError("Uncommitted E141 raw exists; preserve and investigate, never silently overwrite")
                try:
                    blocks = {n: c.bank_from_state(state, "cuda:0").eval().requires_grad_(False) for n, state in group["states"].items()}
                    if any(b.block.top_k != 8 or b.block.num_experts != 64 or b.block.norm_topk_prob for b in blocks.values()): raise ValueError("Original E64/top8/no-renorm program required")
                    chunks = []
                    for index in range(32):
                        budget.check(); h = c.from_bits(hidden[index], "cuda:0"); chunks.append(measure(blocks, h, group["maps"], budget))
                        c.base.emit("E141_support_partition", group=name, sequences=(index + 1) * 16)
                    raw = np.concatenate(chunks)
                    if not np.isfinite(raw).all(): raise ArithmeticError("Nonfinite partition data retained as failure, no filtering")
                    for n, bank in blocks.items():
                        if c.tensor_state_hash(bank.state_dict()) != group["proofs"][n]["full_tensor_sha256"]: raise RuntimeError("Read-only source bank changed")
                    del blocks; torch.cuda.empty_cache()
                    np.savez(path, statistics=raw)
                    assets.write(mp, {"fields": FIELDS, "pairs": [[STUDENTS[l], STUDENTS[r]] for l, r in PAIRS], "rows": group["reference_metadata"]["rows"],
                        "positions_per_sequence": 512, "maps_source_to_seed1": group["maps"], "descriptor": group["descriptor"], "descriptor_sha256": group["descriptor_sha256"], "script_sha256": signature})
                    result["groups"][name] = {"raw": str(path), "raw_sha256": assets.sha(path), "metadata": str(mp), "metadata_sha256": assets.sha(mp),
                        "descriptor_sha256": group["descriptor_sha256"], "source_proofs": group["proofs"], "reference_checks": reference_check(raw, group), "summary": summarize(raw, group["reference_metadata"]["rows"])}
                    result["errors"].pop(name, None)
                except Exception as error:
                    result["errors"][name] = f"{type(error).__name__}: {error}"; result["failures"].append({"group": name, "error": result["errors"][name]}); result["status"] = "partial"; assets.write(args.summary, result); raise
                result["status"] = "partial"; assets.write(args.summary, result)
    result["contrasts"] = contrasts(result["groups"])
    result["status"] = "complete" if set(result["groups"]) == set(GROUPS) and not result["errors"] else "partial"
    assets.write(args.summary, result); return result


def self_test():
    def row(q, f, w):
        f = torch.tensor(f, dtype=torch.bfloat16).reshape(len(q), 2); w = torch.tensor(w, dtype=torch.bfloat16)
        return {"query": torch.tensor(q, dtype=torch.long), "f": f, "w": w, "component": f * w[:, None]}
    def stats(a, b, n=1): return pair_statistics(a, b, n, torch.zeros(n, dtype=torch.long), 1)[0]
    a = row([0], [[1., 2.]], [.5]); empty = row([], [], [])
    x = stats(a, empty); assert x[I["total_SSE"]] == x[I["xor_SSE"]] == 1.25 and x[I["both_SSE"]] == 0
    x = stats(a, row([0], [[2., 4.]], [.5])); assert x[I["content_term_SSE"]] == 1.25 and x[I["gate_term_SSE"]] == 0
    x = stats(a, row([0], [[1., 2.]], [.25])); assert x[I["gate_term_SSE"]] == .3125 and x[I["content_term_SSE"]] == 0
    x = stats(row([0], [[1., 1.]], [1.]), row([0], [[2., 2.]], [.5])); assert x[I["gate_content_cross"]] < 0 and x[I["total_SSE"]] == 0
    b = row([0], [[1.1015625, -2.09375]], [.30078125]); x = stats(a, b)
    assert x[I["product_floor_delta_SSE"]] > 0 and x[I["decomposition_residual_SSE"]] < 1e-25
    assert abs(float(x[I["both_SSE"]] - x[I["ideal_product_delta_SSE"]] - x[I["product_floor_delta_SSE"]] - x[I["ideal_floor_cross"]])) < 1e-14
    x = stats(a, a); assert x[I["total_SSE"]] == x[I["gate_term_SSE"]] == x[I["content_term_SSE"]] == 0
    x = stats(empty, empty); assert pair_numbers(x.numpy(), 1)["both_f_pooled_cosine"] is None
    mapping = np.array([1, 2, 0]); canonical = np.array([3., 7., 11.]); source = canonical[mapping]
    assert np.array_equal(source[np.argsort(mapping)], canonical) and not np.array_equal(source[mapping], canonical)
    students = [row([0], [[1., 0.]], [.5]), row([0], [[2., 0.]], [.5]), row([], [], [])]
    pair_sum = sum(stats(students[l], students[r])[I["total_SSE"]] for l, r in PAIRS) / 9
    dense = torch.tensor([[.5, 0.], [1., 0.], [0., 0.]], dtype=torch.float64)
    assert torch.allclose(pair_sum, (dense - dense.mean(0)).square().sum(-1).mean())
    with tempfile.TemporaryDirectory() as d:
        rows = [{"source": "x", "file_id": str(i // 16)} for i in range(512)]
        raw = np.zeros((512, 64, 3, len(FIELDS))); raw[:, 0, :, I["xor_SSE"]] = 1; raw[:, 0, :, I["total_SSE"]] = 1
        values = draws_for(raw, rows); assert all(v[MAIN[0]] == v[MAIN[1]] and v[MAIN[2]] == 0 for v in values)
        records = {}
        for name, scale in (("free", 1), ("fixed", 2)):
            path = Path(d) / (name + ".npz"); meta = path.with_suffix(".json")
            np.savez(path, statistics=raw * scale); assets.write(meta, {"rows": rows})
            records[name] = {"raw": str(path), "raw_sha256": assets.sha(path), "metadata": str(meta), "metadata_sha256": assets.sha(meta)}
        contrast = contrasts(records)["free_minus_fixed"][MAIN[0]]
        assert contrast["point"] < 0 and contrast["paired_file_ci95"] == [contrast["point"], contrast["point"]]
        fields = [f"pair_seed{l}_seed{r}_SSE" for l, r in PAIRS] + ["cohort_variance"]
        expected = np.concatenate([raw[..., I["total_SSE"]], raw[..., I["total_SSE"]].sum(-1, keepdims=True) / 9], -1)
        ref = Path(d) / "reference.npz"; np.savez(ref, expert=expected)
        group = {"reference": {"raw": str(ref)}, "reference_metadata": {"expert_fields": fields}, "descriptor": {}, "maps": {}}
        assert reference_check(raw, group)["cohort_variance_max_abs_difference"] == 0
        expected[0, 0, 0] += 1; np.savez(ref, expert=expected)
        try: reference_check(raw, group)
        except ArithmeticError: pass
        else: raise AssertionError("Incorrect reference must fail instrument closure")
    return {"passed": True, "CPU_only": True, "hand_support_gate_content": True, "negative_cross": True,
            "BF16_floor_FP64_identity": True, "copy_zero": True, "zero_coverage_undefined": True,
            "non_self_inverse_mapping": True, "pairSum_div9": True, "file_bootstrap_partition": True, "paired_file_CI": True,
            "incorrect_reference_rejected": True, "cuda_initialized": torch.cuda.is_initialized(), "script_sha256": assets.sha(__file__)}


def parser():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--mode", choices=("self-test", "preflight", "evaluate"), default="preflight")
    p.add_argument("--descriptor", type=Path, action="append", default=[]); p.add_argument("--groups", choices=GROUPS, nargs="+", default=["free", "fixed"])
    p.add_argument("--cache-root", type=Path, default=Path("/tmp/xiang-moe-20261025/e135_cache")); p.add_argument("--physical-gpu", type=int, default=3)
    p.add_argument("--budget-file", type=Path, default=Path("/tmp/xiang-moe-20261025/e141_budget.json"))
    p.add_argument("--raw-output", type=Path, default=Path("/tmp/xiang-moe-20261025/e141_support_partition"))
    p.add_argument("--summary", type=Path, default=WB / "results/e141/support_partition.json"); return p


if __name__ == "__main__":
    args = parser().parse_args()
    if args.mode == "self-test": result = self_test()
    elif args.mode == "preflight":
        manifest, hidden, groups = preflight(args); result = {"status": "CPU_preflight_only", "cuda_initialized": torch.cuda.is_initialized(), "script_sha256": assets.sha(__file__),
            "groups": {n: {"descriptor_sha256": g["descriptor_sha256"], "proofs": g["proofs"], "maps": g["maps"]} for n, g in groups.items()}, "held_H_shape": list(hidden.shape)}
    else: result = run(args)
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
