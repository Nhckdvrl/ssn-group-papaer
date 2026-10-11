"""E13: actual subset inference cost, with native full scoring as control."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import torch
from first_wave import RecordedCost, native_info, sync_time, write_json, sha256
from promotion import Calibration, promote, metrics


class SelectiveCost:
    def __init__(self, model, k, mode, fraction, calibration, batch=16, cached=None):
        self.model, self.k, self.mode = model, k, mode
        self.fraction, self.calibration, self.batch = fraction, calibration, batch
        self.cached = cached

    @torch.inference_mode()
    def evaluate(self, info, actions):
        start = sync_time()
        native = self.cached is None and self.mode in ('CHEAP-ALL', 'FULL-REFINE')
        self.model.consistency_loss_weight = float(self.mode == 'FULL-REFINE')
        self.model.action_num_blocks_per_step = [2, 3]
        if self.cached is None:
            direct = self.model.get_cost(info, actions)
            initial = info['predicted_emb'][..., :1, :]
            terminal = info['predicted_emb'][..., -1, :]
        else:
            initial, goal = self.cached
            initial = initial[:, None].expand(1, actions.shape[1], -1, -1)
            predicted = self.model.rollout_action_num_blocks_per_step(initial, actions, [5])
            terminal = predicted[..., -1, :]
            direct = (terminal - goal).square().sum(-1)
        if native:
            score = direct[0].cpu().numpy()
            out = {'elite': np.argsort(score, kind='stable')[:self.k],
                   'selected': int(np.argmin(score)),
                   'queried': np.arange(len(score)) if self.mode == 'FULL-REFINE' else np.array([], dtype=int),
                   'estimated_cost': score}
            return out, {'seconds': sync_time() - start, 'refine_batches': int(self.mode == 'FULL-REFINE')}
        cheap = direct[0].cpu().numpy()
        batches = []

        def query(ids):
            indices = torch.as_tensor(ids, device=actions.device)
            refined = self.model.rollout_action_num_blocks_per_step(
                initial.index_select(1, indices), actions.index_select(1, indices), [2, 3])
            values = direct.index_select(1, indices) + (
                terminal.index_select(1, indices) - refined[..., -1, :]).square().sum(-1)
            batches.append(len(ids))
            return values[0].cpu().numpy()

        budget = None if self.fraction is None else int(np.ceil(self.fraction * len(cheap)))
        out = promote(cheap, query, k=self.k, mode=self.mode, budget=budget,
                      calibration=self.calibration, seed=0, batch=self.batch)
        return out, {'seconds': sync_time() - start, 'refine_batches': len(batches),
                     'query_batch_sizes': batches}


def expand_info(anchor_images, anchor_goal, count):
    return {k: v.unsqueeze(1).expand(1, count, *v.shape[1:])
            for k, v in native_info(anchor_images, anchor_goal).items()}


def run(args):
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    source = Path(args.source)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    cfg = json.loads((source / 'config.json').read_text())
    model = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=False).cuda().eval().requires_grad_(False)
    data = np.load(source / 'anchors.npz')
    banks = [np.load(source / f'candidates_{a:04d}.npz') for a in range(cfg['anchors'])]
    n, k = cfg['candidates'], cfg['elites']
    iterations = sorted(set([0, cfg['iterations'] // 2, cfg['iterations'] - 1]))
    modes = [('CHEAP-ALL', None, 16), ('FULL-REFINE', None, 16),
             ('TOP-M-SCREEN', .2, 16), ('TOP-M-SCREEN', .3, 16), ('TOP-M', .3, 16),
             ('INTERVAL', .2, 16), ('INTERVAL', .3, 16),
             ('LOWER-BOUND', None, 16), ('LOWER-BOUND', None, 64), ('LOWER-BOUND', None, 128)]
    write_json(output / 'config.json', {'source_config': cfg, 'source_data': json.loads((source / 'data_source.json').read_text()),
               'hardware': torch.cuda.get_device_name(), 'modes': modes, 'iterations': iterations,
               'warmup': 2, 'repetitions': args.repetitions, 'seed': args.seed,
               'cache_features': args.cache_features, 'harness_sha256': sha256(__file__)})
    (output / 'timing_audit_used.py').write_text(Path(__file__).read_text())
    # This is a mandatory scoring control, not a method effect experiment.
    a, it = cfg['calibration_anchors'], 0
    actions = torch.tensor(banks[a]['actions'][it][None], device='cuda')
    recorder = RecordedCost(model, 1., [2, 3])
    recorded = recorder.get_cost(expand_info(data['pixels'][a], data['goal_pixels'][a], n), actions)
    model.consistency_loss_weight = 1.
    model.action_num_blocks_per_step = [2, 3]
    native = model.get_cost(expand_info(data['pixels'][a], data['goal_pixels'][a], n), actions)
    control = {'native_wrapper_max_abs': float((native - recorded).abs().max()),
               'saved_bank_max_abs': float(np.max(np.abs(native[0].cpu().numpy() - banks[a]['refined'][it])))}
    write_json(output / 'scoring_control.json', control)
    if not np.allclose(native.cpu().numpy(), recorded.cpu().numpy(), rtol=1e-5, atol=1e-4):
        raise RuntimeError('Native self-consistency scoring control failed')
    if args.cache_features:
        inputs = native_info(data['pixels'][a], data['goal_pixels'][a])
        with torch.inference_mode():
            features = (model.encode({'pixels': inputs['pixels'].cuda()})['emb'],
                        model.encode({'pixels': inputs['goal'].cuda()})['emb'])
        cached_out, _ = SelectiveCost(model,k,'FULL-REFINE',None,None,16,features).evaluate({},actions)
        values = cached_out['estimated_cost']
        control['cached_native_max_abs'] = float(np.max(np.abs(values-native[0].cpu().numpy())))
        if not np.allclose(values,native[0].cpu().numpy(),rtol=1e-5,atol=1e-4):
            raise RuntimeError('Frozen feature cache scoring control failed')
        write_json(output / 'scoring_control.json',control)
    rng = np.random.default_rng(args.seed)
    rows = []
    for a in range(cfg['calibration_anchors'], cfg['anchors']):
        for it in iterations:
            calibration = Calibration.fit([b['cheap'][it] for b in banks[:cfg['calibration_anchors']]],
                                          [b['refined'][it] for b in banks[:cfg['calibration_anchors']]])
            actions = torch.tensor(banks[a]['actions'][it][None], device='cuda')
            pixels, goal = data['pixels'][a], data['goal_pixels'][a]
            cached = None
            encoding_seconds = None
            if args.cache_features:
                start = sync_time()
                inputs = native_info(pixels, goal)
                with torch.inference_mode():
                    initial_emb = model.encode({'pixels': inputs['pixels'].cuda()})['emb']
                    goal_emb = model.encode({'pixels': inputs['goal'].cuda()})['emb']
                cached = (initial_emb, goal_emb)
                encoding_seconds = sync_time() - start
            evaluators = [SelectiveCost(model, k, mode, fraction, calibration, batch, cached)
                          for mode, fraction, batch in modes]
            measurements = [[] for _ in modes]
            for repeat in range(args.repetitions + 2):
                for j in rng.permutation(len(modes)):
                    out, cost = evaluators[j].evaluate(expand_info(pixels, goal, n), actions)
                    if repeat >= 2:
                        measurements[j].append((out, cost))
            for j, (mode, fraction, batch) in enumerate(modes):
                out, cost = measurements[j][-1]
                elapsed = [m[1]['seconds'] for m in measurements[j]]
                row = {'anchor': a, 'iteration': it, 'mode': mode, 'fraction': fraction,
                       'query_batch_limit': batch, 'seconds_median': float(np.median(elapsed)),
                       'encoding_once_seconds': encoding_seconds,
                       'seconds_repetitions': elapsed, 'refine_batches': cost['refine_batches'],
                       **metrics(banks[a]['cheap'][it], banks[a]['refined'][it], banks[a]['actions'][it], out, k)}
                rows.append(row)
                print('timing', a, it, mode, fraction, batch, round(row['seconds_median'], 5),
                      'recall', round(row['elite_recall'], 4), flush=True)
            write_json(output / 'rows.json', rows)
    write_json(output / 'complete.json', {'completed': True, 'scoring_control': control})


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--repetitions', type=int, default=3)
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--cache-features', action='store_true')
    args = p.parse_args()
    try:
        run(args)
    except Exception as exc:
        output = Path(args.output)
        if output.exists():
            write_json(output / 'failure.json', {'exception': type(exc).__name__, 'message': str(exc)})
        raise
