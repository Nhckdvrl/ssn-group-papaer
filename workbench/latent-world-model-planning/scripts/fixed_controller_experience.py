"""H2A: fixed-duration feedback experience; task goal never becomes a subgoal."""
import argparse
import hashlib
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
import intact_multi_seed_source as s
from experience_transfer_control_audit import ROOT, WB, read, save, sha

METHODS = ['OPEN25', 'GOAL5']


def diagnostic(task, env):
    return np.asarray(env._get_obs(), dtype=np.float64) if task == 'tworoom' else a.p.diagnostic(env)


@torch.inference_mode()
def run(task):
    a.setup()
    out = ROOT/f'20261005-E14-fixed-controller-experience-{task}'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__, out/'used.py')
    try:
        features = ROOT/f'20261005-E14-controller-outcome-features-{task}'
        fc = read(features/'config.json')
        assert read(features/'complete.json')['n'] == 1452 and fc['features_sha256'] == sha(features/'features.npz')
        with np.load(features/'features.npz') as raw:
            latent_goal = {(int(j), int(g)):z.copy() for j,g,z in zip(raw['anchor'], raw['branch'], raw['goal'])}
        old = ROOT/'20261004-E20-legal-effect-bank44'
        old_rows = {(r['anchor'], r['branch']):r for r in read(old/'rows.json') if r['task'] == task}
        old_entries = [e for e in read(old/'ledger.json') if e['task'] == task and e['anchor'] < 32]
        memory, memory_images, memory_latents, seen = [], [], [], set()
        for j in range(32):
            for branch in [0]+list(range(2, 12)):
                path = old/f'{task}_{j:03d}_b{branch:02d}.npz'
                assert sha(path) == old_rows[j, branch]['trace_sha256']
                with np.load(path) as raw:
                    image = raw['pixels'][-1].copy()
                image_sha = hashlib.sha256(image.tobytes()).hexdigest()
                if image_sha in seen:
                    continue
                seen.add(image_sha)
                memory.append(dict(id=len(memory), train_source_anchor=j, source_branch=branch, pixel_sha256=image_sha))
                memory_images.append(image)
                memory_latents.append(latent_goal[j, branch])
        memory_images, memory_latents = np.asarray(memory_images), np.asarray(memory_latents)
        np.save(out/'memory_images.npy', memory_images)
        np.save(out/'memory_latents.npy', memory_latents)
        save(out/'memory.json', memory)
        bank = s.bank(task)
        assert read(bank/'complete.json')['n'] == 48
        entries = read(bank/'ledger.json')
        assert [e['anchor'] for e in entries] == list(range(48))
        assert not {e['episode'] for e in entries} & {e['episode'] for e in old_entries}
        net, processor, source = a.source(task, 'cuda')
        assert source == fc['source']
        before = a.state_hash(net.state_dict())
        candidates, controls = [], []
        for entry in entries:
            j = entry['anchor']
            env, warm = a.restore(task, entry)
            assert np.array_equal(warm, np.load(bank/f'history_{j:03d}.npy'))
            full = diagnostic(task, env)
            repeated, warm2 = a.restore(task, entry)
            assert np.array_equal(full, diagnostic(task, repeated)) and np.array_equal(warm, warm2)
            repeated.close()
            actual = [a.diagnostic(task, env)]
            for command in np.load(bank/f'factual_{j:03d}.npy'):
                env.step(command)
                actual.append(a.diagnostic(task, env))
            assert np.array_equal(np.asarray(actual), np.load(bank/f'factual_states_{j:03d}.npy'))
            goal_image = np.load(bank/f'goal_{j:03d}.npy')
            assert np.array_equal(goal_image, env.render())
            env.close()
            zgoal = net.encode(dict(pixels=a.pixels(goal_image[None, None], 'cuda')))['emb'][0, 0].cpu().numpy()
            eligible = np.asarray([k for k,v in enumerate(memory) if v['pixel_sha256'] != hashlib.sha256(goal_image.tobytes()).hexdigest()])
            distance = ((memory_latents-zgoal)**2).mean(-1)
            nearest = eligible[np.argsort(distance[eligible], kind='stable')[:8]]
            remaining = np.setdiff1d(eligible, nearest)
            uniform = np.random.default_rng((131001 if task == 'tworoom' else 131002)+j).choice(remaining, 8, replace=False)
            ids = [-1]+nearest.tolist()+uniform.tolist()
            assert len(ids) == len(set(ids)) == 17
            candidates.append(dict(anchor=j, episode=entry['episode'], memory_ids=ids, final_goal_sha256=sha(bank/f'goal_{j:03d}.npy'), task_goal_state=entry['goal_state']))
            controls.append(dict(anchor=j, warm_exact=True, repeated_full_diagnostic_exact=True, factual_trace_exact=True, goal_pixels_exact=True))
        # Seal proposals for all 48 anchors before collecting any new outcome.
        save(out/'candidates.json', candidates)
        entry = entries[0]
        env, warm = a.restore(task, entry)
        image = memory_images[candidates[0]['memory_ids'][1]]
        inputs = a.info(env.render().copy(), image, entry['warm_actions'], processor, 'cuda')
        full = net.get_action(inputs, horizon=5)
        assert torch.equal(net.get_action(inputs, horizon=1)[:, 0], full[:, 0])
        cpu, cpu_processor, cpu_source = a.source(task, 'cpu')
        assert cpu_source == source
        cpu_plan = cpu.get_action(a.info(env.render().copy(), image, entry['warm_actions'], cpu_processor, 'cpu'), horizon=5)
        np.testing.assert_allclose(full.cpu().numpy(), cpu_plan.numpy(), atol=2e-4, rtol=1e-5)
        del cpu
        env.close()
        save(out/'preflight.json', dict(passed=True, controls=controls, new_query_CPU_CUDA_original_tolerance=True, short_full_first_macro_exact=True, candidates_sealed=True, train_memory_only=True))
        save(out/'config.json', dict(task=task, source=source, methods=METHODS, anchors=48, candidates_per_anchor=17, budget=25, expected_rows=1632, script_sha256=sha(__file__), actor_helper_sha256=sha(a.__file__), candidates_sha256=sha(out/'candidates.json'), memory_images_sha256=sha(out/'memory_images.npy'), memory_latents_sha256=sha(out/'memory_latents.npy'), feature_config_sha256=sha(features/'config.json'), source_bank=str(bank), source_ledger_sha256=sha(bank/'ledger.json'), proposal_seed=131001 if task == 'tworoom' else 131002, hardware=torch.cuda.get_device_name(), collector_ignores_done=True, scope='Fixed25 physical trajectories. Environment final task goal unchanged; subgoals are supplied policy images from TRAIN memory or the given final goal. No subgoal native oracle or future outcome in proposal. Forced continuation after final-goal hit is collection only; live evaluation must absorb at the first native final-goal success. Development48, one source0; unknown pretraining overlap.'))
        rows = []
        for entry, proposal in zip(entries, candidates):
            j = entry['anchor']
            for candidate, mid in enumerate(proposal['memory_ids']):
                goal_image = np.load(bank/f'goal_{j:03d}.npy') if mid == -1 else memory_images[mid]
                first_plan, first_commands, first_state, first_pixels = None, None, None, None
                for method in METHODS:
                    env, warm = a.restore(task, entry)
                    assert np.array_equal(warm, np.load(bank/f'history_{j:03d}.npy'))
                    state, current = diagnostic(task, env), env.render().copy()
                    if first_state is None:
                        first_state, first_pixels = state.copy(), current.copy()
                    assert np.array_equal(state, first_state) and np.array_equal(current, first_pixels)
                    states, images, commands, hits = [state], [current], [], [a.success(task, a.diagnostic(task, env), np.asarray(entry['goal_state']))]
                    past, decisions = list(entry['warm_actions']), []
                    for offset in range(0, 25, 25 if method == 'OPEN25' else 5):
                        raw_previous = np.asarray(past[-5:], dtype=np.float32)
                        plan = net.get_action(a.info(env.render().copy(), goal_image, past, processor, 'cuda'), horizon=5 if method == 'OPEN25' else 1).cpu().numpy().reshape(-1, 2)
                        if offset == 0:
                            if first_plan is None:
                                first_plan = plan.copy()
                            assert np.array_equal(plan[:5], first_plan[:5])
                        issued = processor.scaler.inverse_transform(plan)
                        for command in issued:
                            _, _, done, truncated, _ = env.step(command.astype(np.float32))
                            assert not truncated
                            hit = a.success(task, a.diagnostic(task, env), np.asarray(entry['goal_state']))
                            assert bool(done) == hit
                            commands.append(command)
                            past.append(command)
                            states.append(diagnostic(task, env))
                            hits.append(hit)
                            if len(commands) % 5 == 0:
                                images.append(env.render().copy())
                        decisions.append(dict(step=offset, previous_issued_commands=raw_previous.tolist(), standardized_proposal=plan.tolist()))
                    env.close()
                    assert len(commands) == 25 and len(images) == 6
                    if first_commands is None:
                        first_commands = np.asarray(commands)[:5].copy()
                    assert np.array_equal(np.asarray(commands)[:5], first_commands)
                    path = out/f'trace_{j:03d}_c{candidate:02d}_{method}.npz'
                    np.savez_compressed(path, states=np.asarray(states), commands=np.asarray(commands), observations=np.asarray(images), native_final_goal_hits=np.asarray(hits))
                    rows.append(dict(anchor=j, episode=entry['episode'], candidate=candidate, memory_id=mid, method=method, env_steps=25, native_success_anytime=bool(any(hits)), initial_success=bool(hits[0]), decisions=decisions, trace_sha256=sha(path)))
                    save(out/'rows.json', rows)
            print('H2 fixed-controller experience', task, j, '34 COMPLETE', flush=True)
        assert len(rows) == 1632 and before == a.state_hash(net.state_dict())
        save(out/'complete.json', dict(completed=True, n=1632, model_unchanged=True, new_env_steps=40800))
    except Exception as error:
        save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--task', choices=['tworoom', 'pusht'], required=True)
    run(p.parse_args().task)
