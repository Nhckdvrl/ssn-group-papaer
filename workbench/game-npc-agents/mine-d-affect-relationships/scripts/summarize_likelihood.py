#!/usr/bin/env python3
"""Secondary source-utterance predictability on the unchanged LongEvo sample."""
import argparse,json
from pathlib import Path
from collections import defaultdict
from statistics import mean
from summarize_results import interval

def main():
 a=argparse.ArgumentParser();a.add_argument('--asset-root',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.asset_root);run=root/'runs/D-E02/target_likelihood';m=json.loads((run/'metadata.json').read_text());assert m['complete'];d=json.loads((run/'summary.json').read_text());rows=d['details'];assert len(rows)==256
 by=defaultdict(dict)
 for r in rows:by[r['question_id']][r['mode']]=r
 assert len(by)==64 and all(len(v)==4 for v in by.values());pairs={}
 for baseline in ['base','raw_profile','naive_rewrite']:
  changes=[];book=defaultdict(list);splits=defaultdict(list)
  for q,v in by.items():
   p=v['phase_tree'];b=v[baseline];assert p['target_sha256']==b['target_sha256'] and p['n_target_tokens']==b['n_target_tokens'];delta=p['mean_target_nll']-b['mean_target_nll'];changes.append(dict(question_id=q,corpus=p['corpus'],split=p['split'],delta=delta));book[p['corpus']].append(delta);splits[p['split']].append(delta)
  means={k:mean(v) for k,v in book.items()};pairs['phase_tree-'+baseline]=dict(n=64,corpus_mean_delta=mean(means.values()),by_corpus=means,by_split={s:mean(v) for s,v in splits.items()},descriptive_corpus_bootstrap95=interval(means.values()),lower_tie_higher=[sum(r['delta']<0 for r in changes),sum(r['delta']==0 for r in changes),sum(r['delta']>0 for r in changes)],changes=changes)
 d.update(experiment='D-E02',status='POST-HOC readout registered before computation; initial Char/Sem readouts unchanged',unit='Mean target-content NLL in natural-log nats/token; question-average within corpus then four-corpus macro; lower is better. No EOS, no generated responses, all exact token boundaries verified.',n_model_forwards=256,n_new_generations=0,wall_s=m['wall_s'],model=m['model'],model_revision=m['revision'],paired=pairs)
 Path(args.out).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print(json.dumps(dict(macro=d['corpus_macro'],comparisons={k:{x:y for x,y in v.items() if x!='changes'} for k,v in pairs.items()}),indent=2))
if __name__=='__main__':main()
