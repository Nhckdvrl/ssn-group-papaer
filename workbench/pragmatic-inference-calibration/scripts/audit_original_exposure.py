"""E56 exhaustive original exposure audit; language-only export, no human response."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path('/data1/xiangding/work/pragmatic-inference-calibration')
SRC=ROOT/'parents/noisy-channel-osf-k5vqj/data/GTP2013data'
OUT=Path(__file__).resolve().parents[1]/'results/E56-original-exposure-audit.json'
FIELDS=('Input.trial_','Input.question_1_','CorrectAnswer1')

def load(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def units(rows):
    raw=defaultdict(set); normalized=defaultdict(set)
    for x in rows:
        key=(x['Item'],x['Condition']);t=tuple(x[k] for k in FIELDS)
        raw[key].add(t);normalized[key].add(tuple(v.rstrip() for v in t))
    assert all(len(v)==1 for v in normalized.values()),'semantic variants require independent adjudication'
    return {k:next(iter(v)) for k,v in normalized.items()},[
        {'item':k[0],'condition':k[1],'raw_variants':len(v),'operation':'rstrip only; raw source retained'}
        for k,v in raw.items() if len(v)>1]

def main():
    assert not OUT.exists()
    pairs=[('E1_loc_inversion_raw_data_2013.csv','E6_noise_locative_raw_data_2013.csv'),
        ('E2_DOPOto_raw_data_2013.csv','E7_noise_DOPO_raw_data_2013.csv'),
        ('E3_DOPOfor_raw_data_2013.csv','E8_noise_DOPO_for_raw_data_2013.csv'),
        ('E4_active_passive_raw_data_2013.csv','E9_noise_active_passive_raw_data_2013.csv'),
        ('E5_trans_intrans_raw_data_2013.csv','E10_noise_trans_intrans_raw_data_2013.csv')]
    audit=[];export=[];reference=json.loads((ROOT/'data/E54-original-critical-materials.json').read_text())
    for a,b in pairs:
        pa,pb=SRC/a,SRC/b;ua,wa=units(load(pa));ub,wb=units(load(pb));assert ua.keys()==ub.keys()
        critical=[k for k in ua if k[1]!='filler' and not k[1].endswith(('_v1','_v2'))]
        fillers=[k for k in ua if k[1]=='filler'];controls=[k for k in ua if k not in critical and k not in fillers]
        assert len(critical)==80 and len(fillers)==48 and len(controls)==48
        originals={(x['Item'],x['Condition']):tuple(x[k].rstrip() for k in FIELDS) for x in reference if x['source_file']==a}
        assert originals=={k:ua[k] for k in critical}
        same=sum(ua[k]==ub[k] for k in critical)
        changed=[k for k in fillers if ua[k][0]!=ub[k][0]]
        assert all(ua[k][1:]==ub[k][1:] for k in fillers+controls)
        lexical=[]
        for k in sorted(changed,key=lambda k:int(k[0])):
            lexical.append({'item':k[0],'clean':ua[k][0],'noisy':ub[k][0],
                'word_delta':len(ub[k][0].split())-len(ua[k][0].split())})
        audit.append({'clean':a,'noisy':b,'sha256_clean':sha(pa),'sha256_noisy':sha(pb),
            'critical_same':same,'critical_total':80,'controls_same':sum(ua[k]==ub[k] for k in controls),
            'filler_slots':48,'filler_sentences_changed':len(changed),'filler_question_labels_same':True,
            'whitespace_only_variants':wa+wb,'changed_filler_details':lexical,
            'use_for_fixed_critical_intervention':same==80})
        if same==80:
            for context,u in [('clean',ua),('noisy',ub)]:
                export.append({'source_file':a if context=='clean' else b,'family':a,'context':context,
                    'fillers':[{'Item':k[0],'Condition':k[1],**dict(zip(FIELDS,u[k]))} for k in sorted(fillers,key=lambda k:int(k[0]))],
                    'controls':[{'Item':k[0],'Condition':k[1],**dict(zip(FIELDS,u[k]))} for k in sorted(controls,key=lambda k:(int(k[0]),k[1]))],
                    'critical':[{'Item':k[0],'Condition':k[1],**dict(zip(FIELDS,u[k]))} for k in sorted(critical,key=lambda k:(int(k[0]),k[1]))]})
    # Filler sentence bank is shared across the first four parent alternations.
    for context in ('clean','noisy'):
        groups=[x for x in export if x['context']==context]
        assert len(groups)==4 and all(g['fillers']==groups[0]['fillers'] for g in groups)
    target=ROOT/'data/E56-original-exposure-materials.json';assert not target.exists()
    target.write_text(json.dumps(export,ensure_ascii=False,indent=2)+'\n')
    OUT.write_text(json.dumps({'pairs':audit,'n_fixed_critical':320,'n_contexts':8,
        'export':str(target),'export_sha256':sha(target),
        'history_order_not_human_parity':True,'no_human_answers_exported':True,
        'raw_source_retained':True,'no_noise_cause_isolation_claim':True},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{k:x[k] for k in ('clean','critical_same','filler_sentences_changed','controls_same')} for x in audit]))
if __name__=='__main__':main()
