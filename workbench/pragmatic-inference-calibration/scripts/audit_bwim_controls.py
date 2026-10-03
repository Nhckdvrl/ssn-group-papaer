"""E45 POST-HOC objective geometry diagnostic; never rescoring pragmatic items."""
import argparse,collections,hashlib,json
from pathlib import Path
from bwim_data import prepare

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();episodes,audit=prepare(a.root)
summary=json.loads(Path('workbench/pragmatic-inference-calibration/results/E45-bwim-confidence-summary.json').read_text())
assert summary['full_source_history_gate_pass'] and summary['source_audit']==audit
out={}
for cp,model in summary['models'].items():
    rs=[]
    for fp in model['run_fingerprints']:
        p=a.root/'runs'/fp['run']/'predictions.jsonl'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==fp['raw_sha256']
        rs.extend(json.loads(l) for l in p.read_text().splitlines())
    controls=[r for r in rs if r['trial_type']=='fully_spec'];assert len(controls)==64
    groups=collections.defaultdict(list)
    for r in controls:
        if not r['available']:kind='invalid_or_truncated'
        elif r['correct']:kind='correct'
        else:
            reflected=sorted([[b[0],b[1],b[2],-b[3]] for b in r['parsed']['blocks']])
            kind='incorrect_but_complete_z_reflection_matches' if reflected==r['gold_blocks'] else 'other_incorrect_structure'
        groups[r['list_id'],r['trial_id']].append({'seed':r['seed'],'round':r['round'],'speaker_policy':r['speaker_policy'],
            'diagnostic':kind,'raw_text':r['raw_text'],'terminated_by_eos':r['terminated_by_eos']})
    assert len(groups)==16 and all(len(v)==4 for v in groups.values())
    materials=[]
    for (lst,trial),zs in sorted(groups.items()):
        source=next(r for ep in episodes for r in ep if r['list_id']==lst and r['trial_id']==trial)
        materials.append({'list':lst,'trial':trial,'instruction':source['instruction'],'start':source['start_structure'],
            'target':source['target_structure'],'counts':dict(collections.Counter(z['diagnostic'] for z in zs)),
            'four_unfiltered_control_responses':zs})
    out[cp]={'controls':materials,'counts':dict(collections.Counter(z['diagnostic'] for zs in groups.values() for z in zs))}
a.output.write_text(json.dumps({'post_hoc':True,'models':out,'source_audit':audit,
    'limits':['Diagnostic of all 320 original fully controls; no new GPU/prompt/label and no correct-score modification.',
        'A reflected coordinate match suggests an axis alternative, not an established mechanistic explanation.',
        'Other structural errors require semantic review; root reviewed original16 fully material/14B examples, no independent annotation.',
        'No subset selection to salvage pragmatic findings; overall task-floor failure retained.']},indent=2)+'\n')
print(json.dumps({cp:v['counts'] for cp,v in out.items()}))
