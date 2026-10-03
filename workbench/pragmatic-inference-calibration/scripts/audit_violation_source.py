"""E62 public source audit. No model calls, no participant identifiers exported."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path('/data1/xiangding/work/pragmatic-inference-calibration')
OUT=Path(__file__).resolve().parents[1]/'results/E62-violation-source-audit.json'
TRAITS=['Knowledgeable','Considerate','Competent','Likable']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    result={'experiment':'E62','models_called':0,'experiments':{},'assets':{},
      'limitations':['Released Rev files are retained-participant data; rejected participants and comprehension responses are not included.',
                    'Descriptive arithmetic only; original crossed subject/item mixed models have not been reproduced.',
                    'Same 16 scene identities recur across experiments; 48 is not an independent-scene count.',
                    'Materials are public PDF specifications, not the original running Ibex experiment.']}
    for e,n in [(1,86),(2,93),(3,83)]:
        p=ROOT/'data'/f'E62-exp{e}.csv';rows=list(csv.DictReader(p.open()))
        factor={1:'Relevance',2:'Reason.for.Violation',3:'Preamble'}[e]
        people=defaultdict(list);cells=defaultdict(list);conditions=defaultdict(list)
        for r in rows:
            people[r['subj']].append(r)
            for t in TRAITS:assert r[t].isdigit() and 1<=int(r[t])<=7
            assert abs(float(r['Avg.Comp'])-(int(r['Knowledgeable'])+int(r['Competent']))/2)<1e-12
            assert abs(float(r['Avg.Warmth'])-(int(r['Considerate'])+int(r['Likable']))/2)<1e-12
            cells[int(r['Item']),r[factor],r['Informativeness']].append(r)
            conditions[r[factor],r['Informativeness']].append(r)
        assert len(rows)==n*16 and len(people)==n and len(cells)==64 and len(conditions)==4
        assert all(len(v)==16 and len({r['Item'] for r in v})==16 for v in people.values())
        assert set(k[0] for k in cells)==set(range(1,17))
        means={};norms=[]
        for k,v in sorted(conditions.items()):
            means['/'.join(k)]={t:sum(int(r[t]) for r in v)/len(v) for t in TRAITS}
            for t in TRAITS:assert abs(means['/'.join(k)][t]-np.array([int(r[t]) for r in v]).mean())<1e-12
        for k,v in sorted(cells.items()):
            for t in TRAITS:
                c=Counter(int(r[t]) for r in v)
                norms.append({'scene':k[0],'condition':k[1],'informativeness':k[2],'trait':t,
                              'n':len(v),'counts':[c[i] for i in range(1,8)],
                              'mean':sum(int(r[t]) for r in v)/len(v)})
        text=(ROOT/'data'/f'E62-items-exp{e}.txt').read_text()
        blocks={int(m.group(1)):m.group(2).strip() for m in re.finditer(r'Scenario (\d+)\.\s*(.*?)(?=Scenario \d+\.|\Z)',text,re.S)}
        assert set(blocks)==set(range(1,17))
        result['experiments'][str(e)]={'rows':len(rows),'retained_people':len(people),'recruited_people':100,
            'factor':factor,'n_scene_cells':len(cells),'n_scenes':16,'rater_count_range':[min(map(len,cells.values())),max(map(len,cells.values()))],
            'condition_means':means,'norms':norms,'condition_code_map':sorted(set((r.get('cond',r.get('Condition')),r[factor],r['Informativeness']) for r in rows)),
            'material_specification_flags':{str(i):{'brace_counts':[b.count('{'),b.count('}')],
                    'bracket_counts':[b.count('['),b.count(']')]} for i,b in blocks.items()}}
    for p in sorted((ROOT/'data').glob('E62-*')):
        if p.is_file():result['assets'][p.name]={'sha256':sha(p),'bytes':p.stat().st_size}
    p=ROOT/'papers/violation-social-2023-author.pdf'
    assert p.read_bytes().startswith(b'%PDF')
    result['assets'][p.name]={'sha256':sha(p),'bytes':p.stat().st_size,
       'url':'https://www.langcoglab.com/_files/ugd/7cb05b_a7a6b8309d2f44c1bee5fedacd66d66e.pdf'}
    result['unresolved_material_issues']=[
        'Exp2 scene15 lacks the slash separating reason alternatives; do not guess the original running string.',
        'Exp2 scene16 lacks brackets marking the informativeness manipulation.',
        'Exp3 scene3 contains an extra opening brace; Exp3 scene16 lacks informativeness brackets.',
        'Exp1 vs Exp2 differ in small lexical choices (e.g. scene7 mine/my desk); do not treat cross-experiment strings as exactly matched.',
        'Specifications include spelling errors and missing speaker labels in scene6; no silent correction.']
    result['paper_descriptive_version_discrepancies']=[
        {'comparison':'Exp1 irrelevant Considerate','paper':2.12,'released_raw':float(np.mean([z['mean'] for z in result['experiments']['1']['norms'] if z['condition']=='Irr' and z['trait']=='Considerate'])),
         'note':'Scene-balanced mean differs slightly from pooled mean; both are about 2.22, not 2.12.'},
        {'comparison':'Exp2 unwilling Knowledgeable','paper':2.17,'released_raw':float(np.mean([z['mean'] for z in result['experiments']['2']['norms'] if z['condition']=='Unw' and z['trait']=='Knowledgeable'])),
         'note':'Released raw is about 2.27; no assertion that the mixed-model result is wrong.'}]
    result['source_arithmetic_gate_pass']=True
    OUT.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({e:{k:v[k] for k in ['rows','retained_people','n_scenes','rater_count_range']} for e,v in result['experiments'].items()},indent=2))

if __name__=='__main__':main()
