"""One independent E135 functional capture, using the frozen readout implementation."""
import argparse
import datetime
import socket
import time
from pathlib import Path

from transformers import OlmoeForCausalLM
import torch
import e135_readout as readout

c, assets, WB = readout.c, readout.assets, readout.WB


def run(args):
    if assets.sha(Path(readout.__file__)) != args.readout_sha256:
        raise ValueError('Frozen readout source differs')
    if assets.sha(Path(readout.functions.__file__)) != args.capture_sha256:
        raise ValueError('Frozen functional capture source differs')
    started = time.monotonic()
    manifest, states, proofs, _, _ = readout.preflight(args)
    gpu = c.select_gpu(args.physical_gpu)
    args.raw_output.mkdir(parents=True, exist_ok=True)
    with c.Budget(Path(manifest['budget_file']), 'functional_' + args.condition) as budget:
        model = OlmoeForCausalLM.from_pretrained(
            manifest['model'], dtype=torch.bfloat16, local_files_only=True,
            attn_implementation='sdpa').to('cuda:0').eval().requires_grad_(False)
        model.config.use_cache = False
        original = model.model.layers[9].mlp
        original_hash = c.tensor_state_hash(original.state_dict())
        prefix = c.base.sampled_parameter_hash(model, 'model.layers.9.mlp.')
        if (original_hash != manifest['teacher_block_tensor_sha256']
                or prefix != manifest['teacher_prefix_hash']):
            raise ValueError('Native teacher or prefix differs from cache')
        bank = readout.functions.MeasuredPublic(states[args.condition])
        del states
        bank_hash = c.tensor_state_hash(bank.inner.state_dict())
        path, summary = readout.functions.capture(
            model, original, bank, args.condition, proofs[args.condition],
            manifest, args, budget)
        if (c.tensor_state_hash(original.state_dict()) != original_hash
                or c.base.sampled_parameter_hash(model, 'model.layers.9.mlp.') != prefix
                or c.tensor_state_hash(bank.inner.state_dict()) != bank_hash):
            raise RuntimeError('Read-only functional capture changed parameters')
    return {'experiment': 'E135', 'status': 'complete', 'condition': args.condition,
            'host': socket.gethostname(), 'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'gpu_preflight': gpu, 'seconds': time.monotonic()-started,
            'worker_sha256': assets.sha(__file__), 'readout_sha256': args.readout_sha256,
            'capture_sha256': args.capture_sha256, 'condition_proof': proofs[args.condition],
            'output': str(path), 'output_sha256': summary['output_sha256'],
            'budget_file': manifest['budget_file']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--condition', choices=readout.CONDITIONS, required=True)
    parser.add_argument('--physical-gpu', type=int, required=True)
    parser.add_argument('--readout-sha256', required=True)
    parser.add_argument('--capture-sha256', required=True)
    parser.add_argument('--cache-root', type=Path, default=Path('/tmp/xiang-moe-20261025/e135_cache'))
    parser.add_argument('--student-dir', type=Path, default=Path('/tmp/xiang-moe-20261025/e135_student'))
    parser.add_argument('--plan', type=Path, default=WB/'results/e124/plan.json')
    parser.add_argument('--raw-output', type=Path, default=Path('/tmp/xiang-moe-20261025/e135_readout'))
    args = parser.parse_args()
    try: result = run(args)
    except Exception as error:
        assets.write(WB/f'results/e135/worker_{args.condition}.json', {
            'experiment': 'E135', 'status': 'failed_or_deferred', 'condition': args.condition,
            'error': f'{type(error).__name__}: {error}'})
        raise
    assets.write(WB/f'results/e135/worker_{args.condition}.json', result)
