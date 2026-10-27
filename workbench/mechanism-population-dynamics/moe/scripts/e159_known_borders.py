"""POST-HOC context comparisons, only sealed E155/E156 data; no new forward."""
from pathlib import Path
import hashlib
import json
import numpy as np
import e159_analyze as a

ROOT = Path(__file__).resolve().parents[1]


def asset(path):
    path = Path(path)
    with path.open('rb') as f: digest = hashlib.file_digest(f, 'sha256').hexdigest()
    return {'path': str(path), 'sha256': digest}


def sealed(path):
    m = json.loads(path.read_text())
    if m['status'] != 'complete' or asset(m['raw']['path'])['sha256'] != m['raw']['sha256']:
        raise ValueError('Incomplete/changed inherited raw')
    with np.load(m['raw']['path'], allow_pickle=False) as f: d = {k: f[k].copy() for k in f.files}
    return d, {'manifest': asset(path), 'raw': m['raw']}


def main():
    inherited, cross_proof = sealed(ROOT / 'results/e156/manifest.json')
    cross_manifest = json.loads((ROOT / 'results/e156/manifest.json').read_text())
    natives, proofs = [], []
    for name in ('P','A','B'):
        raw, proof = sealed(ROOT / f'results/e155/manifest_{name}.json')
        native_manifest = json.loads((ROOT / f'results/e155/manifest_{name}.json').read_text())
        i = ('P','A','B').index(name)
        if native_manifest['source_parameter_hash'] != cross_manifest['source_parameter_hashes'][i] or native_manifest['source_buffer_hash'] != cross_manifest['source_buffer_hashes'][i]:
            raise ValueError('The allegedly unchanged source function parameter/buffer bytes differ')
        for k in ('gold','subject','answer_tokens','answer_chars'):
            if not np.array_equal(raw[k], inherited[k]): raise ValueError('Reference population mismatch')
        natives.append(raw['candidate_loglikelihood']); proofs.append(proof)
    native = a.scores(np.stack(natives), inherited['gold'], inherited['answer_tokens'], inherited['answer_chars'])
    cross = a.scores(inherited['candidate_loglikelihood'][:,:,0], inherited['gold'], inherited['answer_tokens'], inherited['answer_chars'])
    common = (inherited['candidate_loglikelihood'][:,:,0].argmax(-1) == inherited['gold']).all((0,1))
    subject = inherited['subject']
    out = {'status':'complete_POST_HOC_inherited_only', 'source_sha256':asset(__file__)['sha256'],
        'inputs':{'E155':proofs, 'E156':cross_proof}, 'new_model_forwards':0,
        'interpretation':'Same source function in native versus P receiver; other branch AND D/G may differ. E159 new borders are needed to isolate partner changes with D/G fixed.',
        'identity':'Removing the transplanted S leaves exact original P D/G/R; removing the transplanted R leaves exact original P D/G/S. Inherited endpoints, not independent observations.',
        'cohort':{'selection':'all nine E156 full source cells raw-correct, before new zeros','total':int(common.sum()),'per_subject':[int((common&(subject==i)).sum()) for i in (0,1)]},
        'metrics':{},'same_correct_decision_counts':{}}
    for metric in native:
        sign = -1 if metric.endswith('accuracy') else 1
        n = native[metric]; x = cross[metric]; stat = lambda v:a.stats(v,subject)
        rows = {}
        for i, source in enumerate(('P','A','B')):
            ns = sign*(n[i,2]-n[i,0]); nr = sign*(n[i,1]-n[i,0])
            ps = sign*(n[0,2]-x[0,i]); pr = sign*(n[0,1]-x[i,0])
            rows[source] = {'native_full_quality':stat(n[i,0]),'S_only_graft_full_quality':stat(x[0,i]),'R_only_graft_full_quality':stat(x[i,0]),
                'native_shared_necessity':stat(ns),'same_S_in_P_receiver_necessity':stat(ps),'native_minus_same_S_receiver_necessity':stat(ns-ps),
                'native_routed_necessity':stat(nr),'same_R_in_P_receiver_necessity':stat(pr),'native_minus_same_R_receiver_necessity':stat(nr-pr)}
        out['metrics'][metric] = rows
    native_hit = native['raw_accuracy'].astype(bool); cross_hit=cross['raw_accuracy'].astype(bool)
    def counts(hit):return {'total':int(hit[common].sum()),'per_subject':[int(hit[common&(subject==i)].sum()) for i in (0,1)]}
    for i, source in enumerate(('P','A','B')):
        out['same_correct_decision_counts'][source]={'native_full':counts(native_hit[i,0]),'S_only_graft_full':counts(cross_hit[0,i]),
            'native_without_S':counts(native_hit[i,2]),'same_S_graft_without_S_inherited_P':counts(native_hit[0,2]),
            'R_only_graft_full':counts(cross_hit[i,0]),'native_without_R':counts(native_hit[i,1]),
            'same_R_graft_without_R_inherited_P':counts(native_hit[0,1])}
    target=ROOT/'results/e159/known_border_posthoc.json'
    target.write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    for metric in ('true_answer_token_NLL','raw_accuracy'):
        print(metric)
        for source in ('A','B'):
            r=out['metrics'][metric][source]
            for name in ('native_minus_same_S_receiver_necessity','native_minus_same_R_receiver_necessity'):
                v=r[name];print(source,name,v['point'],v['question_ci95'])
    print(json.dumps(out['same_correct_decision_counts'],ensure_ascii=False))


if __name__=='__main__':main()
