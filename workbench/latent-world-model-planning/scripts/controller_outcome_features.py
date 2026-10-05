"""H1 frozen visual cache and causal fixed-controller imagination."""
import argparse
import hashlib
import shutil
import numpy as np
import torch
import intact_published_control_v3 as a
from experience_transfer_control_audit import ROOT, WB, read, save, sha

METHODS = ['OPEN25', 'GOAL5', 'REFERENCE5']


def step(model, z, actions, command):
    width = min(model.predictor.pos_embedding.size(1), z.size(1), actions.size(1))
    context = actions[:, -width:].clone()
    context[:, -1] = command
    following = model.predict(z[:, -width:], model.action_encoder(context))[:, -1:]
    return torch.cat([z, following], 1), torch.cat([actions, command[:, None]], 1)


def actor(model, z, target, actions):
    previous = model.action_encoder(actions[:, -1:])[:, -1]
    return model.inverse_action_parameters(z[:, -1], target, previous)['map_mean']


def imagine(world, policy, current, goal, previous, method):
    """The original controller stays fixed even when the world is updated.

    OPEN/REFERENCE plans are formed with the original published world. Future
    GOAL/REFERENCE feedback commands use imagined states, never actual futures.
    """
    z, actions = current[:, None], previous[:, None]
    base_z, base_actions = z, actions
    plans, references = [], [current]
    for _ in range(5):
        command = actor(policy, base_z, goal, base_actions)
        plans.append(command)
        base_z, base_actions = step(policy, base_z, base_actions, command)
        references.append(base_z[:, -1])
    states = [current]
    for k in range(5):
        if method == 'OPEN25' or k == 0:
            command = plans[k]
        elif method == 'GOAL5':
            command = actor(policy, z, goal, actions)
        else:
            command = actor(policy, z, references[k+1], actions)
        z, actions = step(world, z, actions, command)
        states.append(z[:, -1])
    return torch.stack(states, 1), torch.stack(plans, 1), torch.stack(references, 1)


@torch.inference_mode()
def run(task):
    a.setup()
    out = ROOT/f'20261005-E14-controller-outcome-features-{task}'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__, out/'used.py')
    try:
        bank = ROOT/f'20261005-E14-controller-consequence-{task}'
        assert read(bank/'complete.json')['n'] == 1452
        rows = read(bank/'rows.json')
        warm_commands = {e['anchor']:np.asarray(e['warm_actions'][-5:], dtype=np.float32) for e in read(ROOT/'20261004-E20-legal-effect-bank44/ledger.json') if e['task'] == task}
        model, processor, source = a.source(task, 'cuda')
        original = a.state_hash(model.state_dict())
        cache = {}

        def encode(image):
            key = hashlib.sha256(image.tobytes()).hexdigest()
            if key not in cache:
                cache[key] = model.encode(dict(pixels=a.pixels(image[None, None], 'cuda')))['emb'][0, 0].cpu().numpy()
            return cache[key].copy()

        arrays = {k:[] for k in ['z', 'goal', 'previous', 'commands', 'complete_macro', 'frozen', 'anchor', 'branch', 'method', 'steps', 'initial_success', 'success']}
        preflight = None
        for i, row in enumerate(rows):
            path = bank/f"trace_{row['anchor']:03d}_g{row['goal_branch']:02d}_{row['method']}.npz"
            assert sha(path) == row['trace_sha256']
            with np.load(path) as raw:
                images, times = raw['observations'], raw['observation_steps']
                encoded = [encode(image) for image in images]
                target = np.asarray([encoded[0]]+[encoded[int(np.flatnonzero(times == min(k, row['env_steps']))[0])] for k in [5, 10, 15, 20, 25]])
                goal = encode(raw['goal_image'])
                previous_raw = np.asarray(row['decisions'][0]['previous_issued_commands'], dtype=np.float32) if row['decisions'] else warm_commands[row['anchor']]
                previous = processor.scaler.transform(previous_raw).reshape(10).astype(np.float32)
                commands = np.zeros((25, 2), dtype=np.float32)
                if row['env_steps']:
                    commands[:row['env_steps']] = processor.scaler.transform(raw['commands']).astype(np.float32)
                valid = np.arange(1, 6)*5 <= row['env_steps']
                current_t, goal_t, previous_t = [torch.from_numpy(v[None]).cuda() for v in [target[0], goal, previous]]
                predicted, plan, references = imagine(model, model, current_t, goal_t, previous_t, row['method'])
                if row['decisions'] and row['decisions'][0]['kind'] == 'goal':
                    proposal = np.asarray(row['decisions'][0]['standardized_proposal'], dtype=np.float32).reshape(-1, 10)
                    assert np.array_equal(plan[0, :len(proposal)].cpu().numpy(), proposal)
                if preflight is None and row['env_steps'] >= 5:
                    first_image = images[0]
                    inputs = a.info(first_image, raw['goal_image'], previous_raw, processor, 'cuda')
                    direct = model.get_action(inputs, horizon=5)
                    assert torch.equal(direct, plan)
                    assert torch.equal(current_t, model.encode(dict(pixels=inputs['pixels']))['emb'][:, -1])
                    cpu, _, cpu_source = a.source(task, 'cpu')
                    assert cpu_source == source
                    cpu_z = cpu.encode(dict(pixels=a.pixels(first_image[None, None], 'cpu')))['emb'][0, 0].numpy()
                    np.testing.assert_allclose(cpu_z, target[0], atol=2e-4, rtol=1e-5)
                    actual = model.rollout_one_step(current_t[:, None], plan[:, 0], previous_t[:, None])
                    manual = step(model, current_t[:, None], previous_t[:, None], plan[:, 0])
                    assert all(torch.equal(x, y) for x, y in zip(actual, manual))
                    preflight = dict(passed=True, official_plan_exact=True, visual_B1_exact=True, CPU_CUDA_visual_original_tolerance=True, official_world_step_exact=True)
                    del cpu
            for name, value in [('z', target), ('goal', goal), ('previous', previous), ('commands', commands.reshape(5, 10)), ('complete_macro', valid), ('frozen', predicted[0].cpu().numpy()), ('anchor', row['anchor']), ('branch', row['goal_branch']), ('method', METHODS.index(row['method'])), ('steps', row['env_steps']), ('initial_success', row['initial_success']), ('success', row['success'])]:
                arrays[name].append(value)
            if i % 99 == 98:
                print('H1 frozen cache', task, i+1, '/1452', flush=True)
        assert preflight and original == a.state_hash(model.state_dict())
        np.savez_compressed(out/'features.npz', **{k:np.asarray(v) for k, v in arrays.items()})
        save(out/'config.json', dict(task=task, source=source, bank=str(bank), bank_rows_sha256=sha(bank/'rows.json'), bank_config_sha256=sha(bank/'config.json'), script_sha256=sha(__file__), actor_helper_sha256=sha(a.__file__), features_sha256=sha(out/'features.npz'), methods=METHODS, rows=1452, unique_images=len(cache), preflight=preflight, encoder_unchanged=True, train_anchors=list(range(32)), held_anchors=list(range(32, 44)), hardware=torch.cuda.get_device_name(), scope='Frozen B1 visual features. Early success is absorbing only for controller outcomes; complete_macro excludes incomplete physical transitions. Recorded future commands are training labels only, never simulated policy features.'))
        save(out/'complete.json', dict(completed=True, n=1452))
    except Exception as error:
        save(out/'failure.json', dict(type=type(error).__name__, message=str(error)))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', choices=['tworoom', 'pusht'], required=True)
    run(parser.parse_args().task)
