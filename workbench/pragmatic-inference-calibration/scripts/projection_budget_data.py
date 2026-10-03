import hashlib,json
from collections import defaultdict
from projection_data import prepare
from run_iqap_queue import models

def specs(root):
    out=[(cp,mid,sha,'E38-projection-'+cp) for cp,mid,sha in models()]
    out += [(m['id'].split('/')[-1],m['id'],m['sha'],'E39-projection-'+m['id'].split('/')[-1])
        for m in json.loads((root/'models/mistral-stage-manifest.json').read_text())]
    return out

def selected(root,cp):
    spec=next(z for z in specs(root) if z[0]==cp);parent=root/'runs'/spec[3]
    config=json.loads((parent/'config.json').read_text());assert config['complete'] and config['numerical_gate_pass']
    source,audit=prepare(root);assert audit==config['source_audit'];idx={r['id']:r for r in source}
    raw=[json.loads(l) for l in (parent/'predictions.jsonl').read_text().splitlines()]
    assert len(raw)==3520 and len({(z['id'],z['interface']) for z in raw})==3520
    chosen=[];sentinels=set()
    for z in raw:
        r=idx[z['id']]
        if r['human_mean'] is None or z['rating'] is None:continue
        assert all(z[k]==v for k,v in r.items() if k not in ['system_text','user_text','prompt'])
        group=z['interface'],z['task'],z.get('verb','prior')
        if not z['terminated_by_eos']:
            chosen.append({'source':r,'original':z,'selection':'all_numeric_non_eos'})
        elif group not in sentinels:
            chosen.append({'source':r,'original':z,'selection':'first_eos_stratum_sentinel'});sentinels.add(group)
    signature=hashlib.sha256(json.dumps([(z['original']['id'],z['original']['interface'],z['selection']) for z in chosen]).encode()).hexdigest()
    return chosen,{'parent_run':parent.name,'parent_config_sha256':hashlib.sha256((parent/'config.json').read_bytes()).hexdigest(),
        'n':len(chosen),'n_non_eos':sum(z['selection']=='all_numeric_non_eos' for z in chosen),
        'n_sentinels':len(sentinels),'selected_key_sha256':signature,'source_audit':audit}
