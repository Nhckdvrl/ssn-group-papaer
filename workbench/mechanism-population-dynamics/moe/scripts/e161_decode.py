"""POST-HOC decoding diagnostic, preserving E161's original categories and scores."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
import e158_data as data

ROOT = Path(__file__).resolve().parents[1]/'results/e161'


def main():
    plan=json.loads((ROOT/'plan.json').read_text());manifest=json.loads((ROOT/'manifest.json').read_text())
    if manifest['status']!='complete':raise ValueError('Complete result required')
    raw=Path(manifest['raw']['path'])
    if hashlib.sha256(raw.read_bytes()).hexdigest()!=manifest['raw']['sha256']:raise ValueError('Raw identity mismatch')
    a=np.load(raw,allow_pickle=False);m=np.load(plan['outcome_map']['path'],allow_pickle=False)
    queries=json.loads((data.RAW/'queries.json').read_text())['queries']
    tokenizer,meta=data.get_tokenizer();decode=lambda t:tokenizer.decode([int(t)])
    report={'kind':'POST-HOC decoded readout diagnostic after the five-class results were observed',
            'raw_sha256':manifest['raw']['sha256'],'diagnostic_source_sha256':data.sha(Path(__file__)),
            'tokenizer_revision':meta['revision'],'categories_changed':False,'new_model_forwards':0,
            'scope':'Exact existing full-vocabulary top-10 token identities, not continuation generation or semantic relabeling',
            'top1_histograms':{},'rows':[]}
    outcomes=('original','entity_hybrid','relation_hybrid','full_donor')
    for i,model in enumerate(('P','A','B')):
        report['top1_histograms'][model]={}
        for j,path in enumerate(('R','S','RS','attention')):
            report['top1_histograms'][model][path]=dict(Counter(decode(t) for t in a['patched_top_tokens'][i,j,:,:,0].flat))
            for r in range(2):
                for c in range(24):
                    q=int(m['target_query_index'][r,c]);source=int(m['source_query_index_both'][r,c]);labels=m['outcome_token_ids'][:,r,c]
                    top=int(a['patched_top_tokens'][i,j,r,c,0]);hit=np.flatnonzero(labels==top)
                    report['rows'].append({'model':model,'path':path,'relation':r,'country_index':c,
                        'target_query':queries[q],'source_query':queries[source],
                        'labels':{name:{'token_id':int(t),'token_text':decode(t)} for name,t in zip(outcomes,labels)},
                        'category':outcomes[int(hit[0])] if len(hit) else 'other',
                        'top10':[{'token_id':int(t),'text':decode(t)} for t in a['patched_top_tokens'][i,j,r,c]],
                        'native_target_top1':decode(a['native_top_tokens'][i,q,0]),
                        'native_source_top1':decode(a['native_top_tokens'][i,source,0])})
    output=data.RAW.parent/'e161_crossed_entity_relation/decoded_readouts.json'
    output.write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n')
    compact={k:v for k,v in report.items() if k!='rows'}
    compact.update(decoded_rows=len(report['rows']),full_report={'path':str(output),'size_bytes':output.stat().st_size,'sha256':data.sha(output)})
    (ROOT/'decoded_readouts_posthoc.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'complete','decoded_rows':len(report['rows']),'full_report':compact['full_report']},indent=2))


if __name__ == '__main__':
    main()
