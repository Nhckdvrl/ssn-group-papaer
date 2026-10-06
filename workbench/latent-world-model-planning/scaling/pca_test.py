"""Training-free test: CEM with the L2 cost restricted to the top-k PCA subspace of the latent."""
import json, sys
from pathlib import Path
from eval_plan import run
ck, task, offs, ks = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')], [int(x) for x in sys.argv[4].split(',')]
mode = sys.argv[5] if len(sys.argv) > 5 else 'pca'
out = Path(ck).parent / 'eval' / f'{mode}_{Path(ck).stem}.json'
res = json.loads(out.read_text()) if out.exists() else []
done = {(r['offset'], r['pca']) for r in res}
for k in ks:
    for off in offs:
        if (off, k) in done:
            continue
        r = run(ck, task, off, 200, 300, 30, 30, 5, 0, **{mode: k})
        r['pca'] = k
        res.append(r); out.write_text(json.dumps(res))
        print(Path(ck).parent.name, mode, k, 'off', off, 'sr', r['success_rate'], flush=True)
