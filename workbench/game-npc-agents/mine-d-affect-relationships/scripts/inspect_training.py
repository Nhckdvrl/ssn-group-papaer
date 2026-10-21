#!/usr/bin/env python3
"""Keep heterogeneous published training schemas separate from benchmark probes."""
import argparse,json,re
from pathlib import Path
from collections import Counter

def main():
 import pyarrow.parquet as pq
 a=argparse.ArgumentParser();a.add_argument('--dataset',required=True);a.add_argument('--out',required=True);args=a.parse_args();root=Path(args.dataset);result={}
 for p in sorted(root.glob('*/*.parquet')):
  pf=pq.ParquetFile(p);names=pf.schema_arrow.names;kind=p.parent.name
  if kind=='sft':cols=['source','meta_data']
  elif kind=='dpo':cols=['metadata']
  else:cols=['extra_info']
  rows=pq.read_table(p,columns=cols).to_pylist();books=Counter();probes=set();phasecells=set();anchors=Counter()
  for row in rows:
   m=row.get('metadata',row.get('meta_data',row.get('extra_info',{})))
   book=row.get('source') or m.get('source') or m.get('novel')
   if not book:raise ValueError('No explicit book provenance')
   books[book]+=1;pid=m.get('probe_id')
   if pid:probes.add((book,pid));phasecells.add((book,pid,m.get('phase_idx',m.get('anchor_phase_idx'))))
   if 'phase_idx' in m and 'anchor_phase_idx' in m:anchors[str(m['phase_idx']==m['anchor_phase_idx'])]+=1
  result[str(p.relative_to(root))]=dict(n_rows=pf.metadata.num_rows,columns=names,novels=dict(books),n_distinct_probe_ids=len(probes),n_distinct_phase_cells=len(phasecells),current_phase_equals_scene_anchor=dict(anchors))
 selected=['don_quixote','Benjamin_Franklin','Monte_Cristo','Anna_Kareina','He Knew He Was Right','The Odd Women']
 norm=lambda s:re.sub(r'[^a-z0-9]','',s.lower())
 overlap=sorted({b for v in result.values() for b in v['novels'] if norm(b) in {norm(n) for n in selected}})
 assert not overlap,'Selection overlaps public training novels'
 Path(args.out).write_text(json.dumps(dict(configs=result,selected_evaluation_novels=selected,public_training_overlap=overlap,warning='Training test splits are internal configurations. probe anchor phase differs from the current generation phase; neither is a new independent character.'),indent=2,ensure_ascii=False)+'\n')
 print({k:{f:v[f] for f in ['n_rows','novels','n_distinct_probe_ids']} for k,v in result.items()});print('Public training overlap',overlap)
if __name__=='__main__':main()
