"""E37 source-template C edits for all held-out roles; local encoder only."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs', type=Path, default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer
    torch.set_num_threads(1); start = time.monotonic()
    rows = json.loads((args.source / 'research/data/personas/test_100_v3.json').read_text())
    syntax = ast.parse((args.source / 'research/scripts/generate_personas_500.py').read_text())
    descriptions = next(ast.literal_eval(n.value) for n in syntax.body if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == '_BF_DESC' for t in n.targets))
    def text(row):
        return f"{row['age']}세 {row['occupation']}. " + ', '.join(descriptions[f'{k}_{v}'] for k, v in row['big_five'].items()) + '.'
    assert all(text(r) == r['text'] for r in rows)
    pairs = []
    for row in rows:
        original = row['big_five']['C']
        levels = ['high'] if original == 'low' else ['low'] if original == 'high' else ['low', 'high']
        for level in levels:
            changed = copy.deepcopy(row); changed['big_five']['C'] = level; changed['text'] = text(changed)
            assert all(changed[k] == row[k] for k in row if k not in ['big_five', 'text'])
            assert all(changed['big_five'][k] == row['big_five'][k] for k in ['E', 'N', 'A', 'O'])
            pairs.append({'id': row['id'], 'original_C': original, 'target_C': level,
                          'original': row, 'edited': changed})
    assert len(pairs) == 120
    texts = [r['text'] for r in rows] + [p['edited']['text'] for p in pairs]
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    lengths = [len(tok(t)['input_ids']) for t in texts]
    assert max(lengths) <= 256
    (args.out / 'texts.json').write_text(json.dumps({'canonical_ids': [r['id'] for r in rows],
        'pairs': pairs, 'texts': texts, 'token_lengths': lengths}, ensure_ascii=False, indent=2)+'\n')
    model = AutoModel.from_pretrained(args.model, local_files_only=True, dtype=torch.float16).to('cuda').eval().requires_grad_(False)
    vectors = []
    with torch.inference_mode():
        for offset in range(0, len(texts), 32):
            tokens = tok(texts[offset:offset+32], padding=True, truncation=False, return_tensors='pt').to('cuda')
            h = model(**tokens).last_hidden_state
            positions = torch.arange(tokens['attention_mask'].shape[1], device='cuda')
            last = torch.where(tokens['attention_mask'].bool(), positions, -1).max(-1).values
            pooled = h[torch.arange(len(last), device='cuda'), last]
            vectors.append(torch.nn.functional.normalize(pooled, dim=-1).float().cpu().numpy())
    vectors = np.concatenate(vectors)
    np.save(args.out / 'canonical_repeat.npy', vectors[:100]); np.save(args.out / 'C_edits.npy', vectors[100:])
    original = np.load(args.runs / 'e26_semantic_codes/canonical.npy')[400:500].astype(np.float64)
    actual = vectors[:100].astype(np.float64)
    cos = np.sum(actual * original, axis=1) / (np.linalg.norm(actual, axis=1) * np.linalg.norm(original, axis=1))
    result = {'canonical_repeat_cos_mean': float(cos.mean()), 'canonical_repeat_cos_min': float(cos.min()),
         'canonical_cosines': cos.tolist(), 'personas': 100, 'edit_pairs': 120, 'texts_encoded': len(texts),
         'max_token_length': max(lengths), 'model_revision': args.model.name,
         'pooling': 'last real attention-mask token', 'dtype': 'float16; normalized before casting to float32',
         'source_sha': '5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
         'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'text_sha256': hashlib.sha256((args.out / 'texts.json').read_bytes()).hexdigest(),
         'wall_seconds': time.monotonic()-start, 'cloud_calls': 0}
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'canonical_cosines'}), flush=True)


if __name__ == '__main__':
    main()
