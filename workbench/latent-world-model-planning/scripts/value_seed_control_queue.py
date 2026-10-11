"""Use the unchanged controller with explicit full matched-model construction."""
import gc
import json
import shutil
import time
from pathlib import Path
from types import SimpleNamespace
import torch
import matched_learning as m  # Establish the official AD-WM namespace first.
import lewm_pilot
import bounded_control as b


def run():
    roster = [(f'20261004-E14-{arm}-A100-s{seed}', arm, seed)
              for seed in [1,2] for arm in ['VGIQL-JOINT','VGIQL-SEPARATE']]
    for source, arm, seed in roster:
        while not (m.ROOT/source/'complete.json').exists():
            if (m.ROOT/source/'failure.json').exists() or (Path('/tmp/latent-wm-runs')/source/'failure.json').exists():
                raise RuntimeError(f'Locked training failed: {source}; no survivor replacement')
            print('waiting_for_fixed_endpoint', source, flush=True)
            time.sleep(30)
        complete = json.loads((m.ROOT/source/'complete.json').read_text())
        assert complete == dict(completed=True, training_updates=5650, simulator_episodes=0)
        cfg = json.loads((m.ROOT/source/'config.json').read_text())
        assert cfg['script_sha256'] == m.digest(m.__file__) and cfg['arm'] == arm and cfg['seed'] == seed
        checkpoint = m.HF/source/'u5650.ckpt'
        assert m.digest(checkpoint) == json.loads((m.ROOT/source/'summary.json').read_text())['checkpoint_sha256']
        for interface in ['physical', 'native']:
            output = Path('/tmp/latent-wm-runs')/f'20261005-value-repeat-control-{arm}-s{seed}-{interface}-RTX'
            args = SimpleNamespace(bank='/tmp/latent-wm-runs/20261004-E20-fresh-control-bank48',
                output=str(output), checkpoint=str(checkpoint), interface=interface)
            original = lewm_pilot.architecture
            # m.architecture was captured at module import, before this override.
            def architecture(config):
                model, _ = m.make_model(config, seed, arm)
                assert model.residual_target == (arm in ['RESIDUAL', 'FULL-AD'])
                assert len(model.state_dict()) == (321 if arm == 'FULL-AD' else 303)
                return model
            lewm_pilot.architecture = architecture
            try:
                b.evaluate(args)
                context = dict(arm=arm, seed=seed, source_training_run=source,
                    train_checkpoint_sha256=m.digest(checkpoint), loader_sha256=m.digest(__file__),
                    namespace='official AD-WM; strict checkpoint load with complete residual/inverse/MI schema',
                    scope='matched constant-LR development; three value train sources retained; not original-paper numeric reproduction')
                b.save(output/'matched_loader.json', context)
                shutil.copy2(output/'matched_loader.json', m.ROOT/output.name/'matched_loader.json')
            except Exception as error:
                if output.exists(): b.save(output/'failure.json', dict(type=type(error).__name__, message=str(error)))
                raise
            finally:
                lewm_pilot.architecture = original
            gc.collect(); torch.cuda.empty_cache()


if __name__ == '__main__': run()
