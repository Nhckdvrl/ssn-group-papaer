"""E00/E13 A0/E16 Stage 0 on the released Fast-LeWM and native simulators.

No training framework: the native CEM solver is retained and its cost calls are
recorded. Large candidate/branch artifacts go to --output, outside tracked git.
"""
import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

os.environ.setdefault("MUJOCO_GL", "egl")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import numpy as np
import torch
from promotion import Calibration, promote, metrics as promotion_metrics

WB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WB / "vendor/fast-lewm"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    def convert(x):
        if isinstance(x, (np.ndarray, torch.Tensor)):
            return x.tolist()
        if isinstance(x, np.generic):
            return x.item()
        if isinstance(x, Path):
            return str(x)
        raise TypeError(type(x).__name__)
    Path(path).write_text(json.dumps(value, default=convert, indent=2, allow_nan=False) + "\n")


def sync_time():
    torch.cuda.synchronize()
    return time.perf_counter()


def image_tensor(images):
    x = torch.as_tensor(np.asarray(images)).float()
    if x.shape[-1] == 3:
        x = x.movedim(-1, -3)
    x = x / 255
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    return (x - mean) / std


def native_info(pixels, goal):
    # Shape expected by native solve before it expands the candidate dimension.
    return {"pixels": image_tensor([pixels]).unsqueeze(0),
            "goal": image_tensor([goal]).unsqueeze(0),
            "action": torch.zeros(1, 1, 2)}


def simulator_state(env, info=None):
    # PushT's info exposes positions separately, unlike TwoRoom's state key.
    if info is not None and "state" in info:
        return np.asarray(info["state"]).copy()
    return np.asarray(env._get_obs()).copy()


def native_anchors(path, count, seed, goal_offset=25):
    import h5py
    import hdf5plugin  # Registers the original compression filters.
    with h5py.File(path, "r") as f:
        lengths, offsets = f["ep_len"][:], f["ep_offset"][:]
        # Separate entire source episodes, so calibration never shares a trajectory.
        valid = np.flatnonzero(lengths > goal_offset + 1)
        chosen = np.random.default_rng(seed).choice(valid, count, replace=False)
        actions = f["action"][:]
        actions = actions[np.isfinite(actions).all(1)]
        action_mean, action_std = actions.mean(0), actions.std(0)
        anchors = []
        rng = np.random.default_rng(seed + 1000)
        for ep in chosen:
            start = int(rng.integers(0, int(lengths[ep]) - goal_offset))
            row = int(offsets[ep]) + start
            state_key = "state" if "state" in f else "proprio"
            anchors.append({"episode": int(ep), "start": start,
                "state": f[state_key][row], "goal_state": f[state_key][row + goal_offset],
                "pixels": f["pixels"][row], "goal_pixels": f["pixels"][row + goal_offset],
                "factual_suffix": f["action"][row:row + goal_offset],
                "factual_states": f[state_key][row:row + goal_offset + 1]})
    return anchors, action_mean, action_std, {"source": "official_hdf5", "file": Path(path).name,
                                            "sha256": sha256(path)}


def generated_anchors(env, task, count, seed):
    """Engineering fallback during download; explicitly not numeric reproduction.

    Goals come from actual simulator trajectories, not imagined model states.
    This does not reuse the original dataset action-normalization statistics.
    """
    rng = np.random.default_rng(seed + 5000)
    anchors, action_samples = [], []
    for ep in range(count):
        env.reset(seed=seed + ep)
        if task == "tworoom":
            from stable_worldmodel.envs.two_room.expert_policy import ExpertPolicy
            expert = ExpertPolicy(seed=seed + ep)
            expert.set_env(env)
        frames, states, actions = [], [], []
        for t in range(51):
            info = env._get_info()
            frames.append(env.render())
            states.append(simulator_state(env, info))
            if t == 50:
                break
            if task == "tworoom":
                a = expert.get_action(info)
            else:
                a = rng.uniform(-1, 1, 2)
                target = np.asarray(env.agent.position) + 100 * a
                target = np.clip(target, np.asarray(env.block.position) - 100,
                                 np.asarray(env.block.position) + 100)
                a = np.clip((target - np.asarray(env.agent.position)) / 100, -1, 1)
            actions.append(np.asarray(a).copy())
            env.step(a)
        action_samples.extend(actions)
        # Fixed offset and start, independent of all model scores and success.
        start = ep % 10
        anchors.append({"episode": ep, "start": start, "state": states[start],
            "goal_state": states[start + 25], "pixels": frames[start],
            "goal_pixels": frames[start + 25], "reset_seed": seed + ep,
            "factual_prefix": np.asarray(actions[:start]),
            "factual_suffix": np.asarray(actions[start:start + 25]),
            "factual_states": np.asarray(states[start:start + 26])})
    actions = np.asarray(action_samples)
    return anchors, actions.mean(0), actions.std(0), {
        "source": "simulator_generated_engineering", "steps": len(action_samples),
        "limitation": "different dataset and action normalization; not published-protocol reproduction"}


def restore(env, anchor, seed):
    if "factual_prefix" in anchor:
        # Replay the factual prefix from a fresh reset to recover hidden physics
        # state as well as publicly visible coordinates, without new dynamics.
        env.reset(seed=anchor["reset_seed"])
        for action in anchor["factual_prefix"]:
            env.step(action)
        env._set_goal_state(np.asarray(anchor["goal_state"]).copy())
        return
    # Released dataset evaluation: fresh reset followed by public setters.
    env.reset(seed=seed)
    env._set_state(np.asarray(anchor["state"]).copy())
    env._set_goal_state(np.asarray(anchor["goal_state"]).copy())


def factual_replay_audit(env, anchors, output, seed):
    rows = []
    for a, anchor in enumerate(anchors):
        restore(env, anchor, seed + a)
        states = [simulator_state(env, env._get_info())]
        flags = []
        for action in anchor["factual_suffix"]:
            _, _, done, truncated, info = env.step(action)
            states.append(simulator_state(env, info))
            flags.append([bool(done), bool(truncated)])
        error = np.asarray(states) - anchor["factual_states"]
        rows.append({"anchor": a, "source_episode": anchor["episode"],
            "macro_horizon_state_l2": np.linalg.norm(error[::5], axis=1).tolist(),
            "state_max_abs": float(np.abs(error).max()), "final_success": flags[-1][0],
            "success_any": any(f[0] for f in flags), "env_steps": len(flags),
            "retains_post_terminal_for_replay_audit": True})
    write_json(output / "factual_replay_audit.json", rows)
    print("factual_replay", "max_state_abs", max(r["state_max_abs"] for r in rows),
          "positive_success", sum(r["final_success"] for r in rows), "/", len(rows), flush=True)
    return rows


class RecordedCost:
    def __init__(self, model, beta, blocks, capture=True):
        self.model, self.beta, self.blocks = model, beta, blocks
        self.capture = capture
        self.banks = []
        self.timings = []

    @torch.inference_mode()
    def get_cost(self, info, actions):
        self.model.consistency_loss_weight = 0.0
        start = sync_time()
        direct = self.model.get_cost(info, actions)
        direct_time = sync_time() - start
        initial = info["predicted_emb"][..., :1, :]
        terminal = info["predicted_emb"][..., -1, :]
        start = sync_time()
        decomposed = self.model.rollout_action_num_blocks_per_step(initial, actions, self.blocks)
        residual = (terminal - decomposed[..., -1, :]).square().sum(-1)
        refine_time = sync_time() - start
        refined = direct + self.beta * residual
        if self.capture:
            self.banks.append({"actions": actions[0].cpu().numpy(),
                "cheap": direct[0].cpu().numpy(), "refined": refined[0].cpu().numpy(),
                "direct_goal": direct[0].cpu().numpy(),
                "decomposed_goal": (decomposed[..., -1, :] - info["goal_emb"][:, -1:, :]).square().sum(-1)[0].cpu().numpy(),
                "terminal": terminal[0].cpu().numpy(), "initial": initial[0, :1].cpu().numpy(),
                "direct_seconds": direct_time, "refine_seconds": refine_time})
        self.timings.append([direct_time, refine_time])
        return refined


def score_audit(banks, calibration_count, k, output, seed):
    calibration_banks = [b for b in banks if b["anchor"] < calibration_count]
    test_banks = [b for b in banks if b["anchor"] >= calibration_count]
    rows = []
    modes = ["CHEAP-ALL", "FULL-REFINE", "LOWER-BOUND", "RANDOM-M", "TOP-M",
             "TOP-M-SCREEN", "TOP-M-MIXED", "ELITE-BAND", "INTERVAL"]
    for iteration in sorted({b["iteration"] for b in banks}):
        fit = [b for b in calibration_banks if b["iteration"] == iteration]
        cal = Calibration.fit([b["cheap"] for b in fit], [b["refined"] for b in fit])
        for b in [x for x in test_banks if x["iteration"] == iteration]:
            for mode in modes:
                fractions = [None] if mode in modes[:3] else [0.1, 0.2, 0.3, 0.5, 1.0]
                for fraction in fractions:
                    budget = None if fraction is None else int(np.ceil(fraction * len(b["cheap"])))
                    start = time.perf_counter()
                    result = promote(b["cheap"], lambda ids: b["refined"][ids], k=k,
                        mode=mode, budget=budget, calibration=cal,
                        seed=seed + 100000 * b["anchor"] + iteration)
                    row = {"anchor": b["anchor"], "iteration": iteration, "mode": mode,
                        "requested_fraction": fraction, "selector_cpu_seconds": time.perf_counter() - start,
                        **promotion_metrics(b["cheap"], b["refined"], b["actions"], result, k)}
                    lo, _, hi = cal.intervals(b["cheap"])
                    row["calibration_coverage"] = float(np.mean((b["refined"] >= lo) & (b["refined"] <= hi)))
                    rows.append(row)
    write_json(output / "e13_rows.json", rows)
    summary = []
    for mode in modes:
        for fraction in [None] if mode in modes[:3] else [0.1, 0.2, 0.3, 0.5, 1.0]:
            subset = [r for r in rows if r["mode"] == mode and r["requested_fraction"] == fraction]
            keys = [key for key in subset[0] if key not in ("mode", "anchor", "iteration", "requested_fraction")]
            avg = {key: float(np.mean([r[key] for r in subset])) for key in keys}
            # Episodes are the resampling unit; CEM banks are correlated within episode.
            episode_means = {a: {key: np.mean([r[key] for r in subset if r["anchor"] == a]) for key in keys}
                             for a in sorted({r["anchor"] for r in subset})}
            e = list(episode_means.values())
            rng = np.random.default_rng(seed + 9000)
            inds = rng.integers(0, len(e), (2000, len(e)))
            ci = {key: np.quantile(np.asarray([v[key] for v in e])[inds].mean(1), [0.025, 0.975]).tolist() for key in keys}
            summary.append({"mode": mode, "requested_fraction": fraction, "banks": len(subset),
                            "episodes": len(e), "mean": avg, "episode_bootstrap_ci95": ci})
    return summary


def branch_bank(env, anchors, banks, action_mean, action_std, k, output, seed):
    """Hidden branches are persisted separately from public pre-query predictions."""
    import h5py
    rng = np.random.default_rng(seed + 8000)
    records = []
    with h5py.File(output / "hidden_branches.h5", "w") as hidden:
        for anchor_id, anchor in enumerate(anchors):
            if anchor_id < 4:
                continue
            b = next(x for x in reversed(banks) if x["anchor"] == anchor_id)
            # Uniform reference branches and competing model candidates, fixed before replay.
            competing = np.argsort(b["cheap"], kind="stable")[:4]
            remaining = np.setdiff1d(np.arange(len(b["cheap"])), competing)
            ids = np.concatenate((competing, rng.choice(remaining, 4, replace=False)))
            entry = hidden.create_group(str(anchor_id))
            for candidate_id in ids:
                actions = b["actions"][candidate_id].reshape(25, 2) * action_std + action_mean
                states, frames, terminated_flags = [], [], []
                start = time.perf_counter()
                restore(env, anchor, seed + anchor_id)
                states.append(simulator_state(env, env._get_info()))
                frames.append(env.render())
                for action in actions:
                    _, _, terminated, truncated, info = env.step(action)
                    states.append(simulator_state(env, info))
                    frames.append(env.render())
                    terminated_flags.append([terminated, truncated])
                group = entry.create_group(str(candidate_id))
                group.create_dataset("actions", data=actions)
                group.create_dataset("states", data=np.asarray(states))
                group.create_dataset("pixels", data=np.asarray(frames), compression="gzip", compression_opts=1)
                group.create_dataset("done", data=np.asarray(terminated_flags))
                group.attrs["steps"] = len(actions)
                # Full prefix is retained after termination for open-loop outcome audit only.
                group.attrs["post_terminal_steps_retained"] = True
                replay_errors = []
                if candidate_id == ids[0]:
                    for _ in range(3):
                        restore(env, anchor, seed + anchor_id)
                        replay_states = [simulator_state(env, env._get_info())]
                        replay_frames = [env.render()]
                        for action in actions:
                            _, _, _, _, info = env.step(action)
                            replay_states.append(simulator_state(env, info))
                            replay_frames.append(env.render())
                        replay_errors.append({"state_max_abs": float(np.max(np.abs(np.asarray(replay_states) - np.asarray(states)))),
                            "pixel_mae": float(np.mean(np.abs(np.asarray(replay_frames, dtype=float) - np.asarray(frames, dtype=float))))})
                records.append({"anchor": anchor_id, "candidate": int(candidate_id),
                    "steps": len(actions), "reset_count": 1 + len(replay_errors),
                    "restore_prefix_steps": len(anchor.get("factual_prefix", [])) * (1 + len(replay_errors)),
                    "replay": replay_errors, "seconds": time.perf_counter() - start})
                print("branch", anchor_id, candidate_id, "replay", replay_errors, flush=True)
    return records


def train_steps(model, output, batch_size, steps, seed):
    """Real acquired simulator transitions; original prefix/SIGReg objective, E00 only."""
    import h5py
    from module import SIGReg
    clips = []
    read_start = time.perf_counter()
    with h5py.File(output / "hidden_branches.h5", "r") as f:
        for anchor in f.values():
            for b in anchor.values():
                clips.append((b["pixels"][::5], b["actions"][:]))
    disk_read_seconds = time.perf_counter() - read_start
    rng = np.random.default_rng(seed)
    model = copy.deepcopy(model).train().requires_grad_(True)
    # Original model checkpoint remains untouched by throughput-only updates.
    reg = SIGReg(knots=17, num_proj=1024, merge_time_into_batch=False).cuda()
    optim = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=1e-3)
    timings, loads, losses = [], [], []
    torch.cuda.reset_peak_memory_stats()
    for step in range(steps + 5):
        start = time.perf_counter()
        picks = rng.choice(len(clips), batch_size, replace=True)
        images = image_tensor(np.stack([clips[p][0] for p in picks])).cuda()
        act = torch.tensor(np.stack([clips[p][1] for p in picks]), dtype=torch.float32).cuda()
        norm = np.load(output / "action_normalization.npz")
        act = (act - torch.tensor(norm["mean"], device="cuda", dtype=torch.float32)) / torch.tensor(norm["std"], device="cuda", dtype=torch.float32)
        act = act.reshape(batch_size, 5, 10)
        loads.append(sync_time() - start)
        optim.zero_grad(set_to_none=True)
        start = sync_time()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            encoded = model.encode({"pixels": images, "action": act})
            pred = model.predict(encoded["emb"][:, 0], encoded["act_emb"][:, :5])
            pred_loss = model.prediction_loss(pred, encoded["emb"][:, 1:6])
            reg_loss = reg(encoded["emb"].transpose(0, 1))
            loss = pred_loss + 0.09 * reg_loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1)
        optim.step()
        timings.append(sync_time() - start)
        losses.append(float(loss.detach()))
        if not np.isfinite(losses[-1]):
            raise RuntimeError("Nonfinite E00 training loss")
        print("train_step", step, "loss", losses[-1], "seconds", timings[-1], flush=True)
    return {"batch_size": batch_size, "warmup": 5, "measured_steps": steps,
        "step_seconds_median": float(np.median(timings[5:])), "load_seconds_median": float(np.median(loads[5:])),
        "all_step_seconds": timings, "all_load_seconds": loads, "losses": losses,
        "peak_vram_gib": torch.cuda.max_memory_allocated() / 2**30,
        "initial_disk_read_seconds": disk_read_seconds,
        "load_timing_scope": "in-memory batch preparation and H2D, excludes initial disk read",
        "training_source": "E16 acquired native simulator branches; throughput only, not reproduction"}


def run(args):
    import gymnasium as gym
    import stable_worldmodel as swm
    from gymnasium.vector.utils import batch_space
    from jepa import JEPA  # Required for official object checkpoint unpickling.
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    packages = {n: importlib.metadata.version(n) for n in ["torch", "torchvision", "numpy", "transformers", "stable-worldmodel"]}
    config = vars(args).copy()
    config.update({"packages": packages, "hardware": torch.cuda.get_device_name(),
                   "harness_sha256": sha256(__file__),
                   "fast_lewm_commit": subprocess.check_output(["git", "-C", str(WB / "vendor/fast-lewm"), "rev-parse", "HEAD"], text=True).strip()})
    # Never expose internal hostname/address in checked-in result metadata.
    write_json(output / "config.json", config)
    (output / "first_wave_used.py").write_text(Path(__file__).read_text())
    checkpoint = Path(args.checkpoint)
    start = time.perf_counter()
    model = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model.to("cuda").eval().requires_grad_(False)
    torch.cuda.synchronize()
    load_seconds = time.perf_counter() - start
    if not isinstance(model, JEPA):
        raise TypeError(f"Expected official JEPA, found {type(model)}")
    state_dict = model.state_dict()
    if not all(torch.isfinite(t).all() for t in state_dict.values()):
        raise RuntimeError("Nonfinite checkpoint tensors")
    load_report = {"seconds": load_seconds, "sha256": sha256(checkpoint), "bytes": checkpoint.stat().st_size,
        "parameters": sum(p.numel() for p in model.parameters()), "state_dict_keys": len(state_dict),
        "missing_unexpected_keys": "object checkpoint, no independent weights reference supplied",
        "parameter_finiteness": True}
    print("loaded", args.task, load_report, flush=True)
    write_json(output / "checkpoint_load.json", load_report)
    env = gym.make("swm/TwoRoom-v1" if args.task == "tworoom" else "swm/PushT-v1", render_mode="rgb_array").unwrapped
    if args.dataset:
        anchors, action_mean, action_std, source = native_anchors(args.dataset, args.anchors, args.seed)
    elif args.generated:
        anchors, action_mean, action_std, source = generated_anchors(env, args.task, args.anchors, args.seed)
    else:
        raise ValueError("Supply --dataset, or explicitly --generated for engineering fallback")
    action_std = np.maximum(action_std, 1e-6)
    write_json(output / "data_source.json", source)
    np.savez(output / "action_normalization.npz", mean=action_mean, std=action_std)
    np.savez_compressed(output / "anchors.npz",
        states=np.stack([a["state"] for a in anchors]),
        goal_states=np.stack([a["goal_state"] for a in anchors]),
        pixels=np.stack([a["pixels"] for a in anchors]),
        goal_pixels=np.stack([a["goal_pixels"] for a in anchors]),
        episodes=np.asarray([a["episode"] for a in anchors]),
        starts=np.asarray([a["start"] for a in anchors]))
    factual_replay_audit(env, anchors, output, args.seed)
    torch.cuda.reset_peak_memory_stats()
    banks, alignment, planner_times = [], [], []
    # The simulator hidden state stays entirely out of model/selector input.
    space = batch_space(env.action_space, 1)
    plan_config = swm.PlanConfig(horizon=1, receding_horizon=1, action_block=25, warm_start=True)
    for anchor_id, anchor in enumerate(anchors):
        restore(env, anchor, args.seed + anchor_id)
        actual = env.render()
        alignment.append(float(np.mean(np.abs(actual.astype(float) - np.asarray(anchor["pixels"], dtype=float)))))
        recorder = RecordedCost(model, 1.0, [2, 3])
        solver = swm.solver.CEMSolver(recorder, batch_size=1, num_samples=args.candidates,
            topk=args.elites, n_steps=args.iterations, device="cuda", seed=args.seed + anchor_id)
        solver.configure(action_space=space, n_envs=1, config=plan_config)
        start = sync_time()
        planned = solver.solve(native_info(anchor["pixels"], anchor["goal_pixels"]))
        planner_times.append(sync_time() - start)
        for iteration, b in enumerate(recorder.banks):
            b.update({"anchor": anchor_id, "iteration": iteration})
            banks.append(b)
        # Persist every bank; no survivorship selection of candidate populations.
        np.savez_compressed(output / f"candidates_{anchor_id:04d}.npz",
            actions=np.stack([b["actions"] for b in recorder.banks]),
            cheap=np.stack([b["cheap"] for b in recorder.banks]),
            refined=np.stack([b["refined"] for b in recorder.banks]),
            direct_goal=np.stack([b["direct_goal"] for b in recorder.banks]),
            decomposed_goal=np.stack([b["decomposed_goal"] for b in recorder.banks]),
            initial=np.stack([b["initial"] for b in recorder.banks]),
            terminal=np.stack([b["terminal"] for b in recorder.banks]))
        print("anchor", anchor_id, "planner_seconds", planner_times[-1], "restore_pixel_mae", alignment[-1], flush=True)
    audit = score_audit(banks, args.calibration_anchors, args.elites, output, args.seed)
    write_json(output / "e13_summary.json", audit)
    print("e13_summary", json.dumps([{k:v for k,v in r.items() if k != "episode_bootstrap_ci95"} for r in audit]), flush=True)
    branch_records = branch_bank(env, anchors, banks, action_mean, action_std, args.elites, output, args.seed)
    write_json(output / "e16_summary.json", {"records": branch_records,
        "total_env_steps": sum(r["steps"] * r["reset_count"] for r in branch_records),
        "total_restore_prefix_steps": sum(r["restore_prefix_steps"] for r in branch_records),
        "branch_count": len(branch_records), "total_resets": sum(r["reset_count"] for r in branch_records),
        "hidden_file_sha256": sha256(output / "hidden_branches.h5"),
        "stage": "restore/replay instrumentation only; no acquisition-effect claim"})
    # Full episode on the native simulator, reference planner and original success test.
    anchor = anchors[args.calibration_anchors]
    restore(env, anchor, args.seed + args.calibration_anchors)
    episode_started = sync_time()
    episode_success = False
    times = []
    executed_steps = 0
    for episode_step in range(0, 50, 25):
        recorder = RecordedCost(model, 1.0, [2, 3], capture=False)
        solver = swm.solver.CEMSolver(recorder, batch_size=1, num_samples=args.candidates,
            topk=args.elites, n_steps=args.iterations, device="cuda", seed=args.seed + episode_step)
        solver.configure(action_space=space, n_envs=1, config=plan_config)
        start = sync_time()
        solved = solver.solve(native_info(env.render(), anchor["goal_pixels"]))
        times.append(sync_time() - start)
        actions = solved["actions"][0].numpy().reshape(25, 2) * action_std + action_mean
        for action in actions:
            _, _, done, truncated, info = env.step(action)
            executed_steps += 1
            episode_success |= bool(done)
            if done or truncated:
                break
        if done or truncated:
            break
    summary = {"task": args.task, "checkpoint": load_report, "source": source,
        "restore_pixel_mae": alignment, "planner_seconds": planner_times,
        "first_episode": {"env_steps": executed_steps, "success_at_any_step": episode_success,
                          "success_final_step": bool(done), "seconds": sync_time() - episode_started,
                          "planning_seconds": times, "ci": "one episode, no performance CI"},
        "inference_peak_vram_gib": torch.cuda.max_memory_allocated() / 2**30,
        "bank_count": len(banks), "candidate_count": args.candidates,
        "calibration_episodes": args.calibration_anchors, "audit_episodes": args.anchors - args.calibration_anchors}
    write_json(output / "e00_summary.json", summary)
    if args.train_steps:
        training = train_steps(model, output, args.batch_size, args.train_steps, args.seed)
        write_json(output / "e00_train.json", training)
    write_json(output / "complete.json", {"completed": True})
    env.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--task", choices=["tworoom", "pusht"], required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--dataset")
    p.add_argument("--generated", action="store_true")
    p.add_argument("--output", required=True)
    p.add_argument("--anchors", type=int, default=12)
    p.add_argument("--calibration-anchors", type=int, default=4)
    p.add_argument("--candidates", type=int, default=300)
    p.add_argument("--elites", type=int, default=30)
    p.add_argument("--iterations", type=int, default=30)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--train-steps", type=int, default=20)
    p.add_argument("--batch-size", type=int, default=16)
    a = p.parse_args()
    if not 4 <= a.calibration_anchors < a.anchors:
        p.error("need 4+ separate calibration episodes and held-out audit episodes")
    try:
        run(a)
    except Exception as exc:
        out = Path(a.output)
        if out.exists():
            write_json(out / "failure.json", {"error": type(exc).__name__, "message": str(exc)})
        raise
