"""Create the frozen E01R development/confirmation split from the pinned CSV."""
import argparse,ast,csv,hashlib,json,pathlib,random

ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--csv',type=pathlib.Path,required=True); args=ap.parse_args()
    cfg=json.loads((ROOT/'configs/e01r.json').read_text())
    data=args.csv.read_bytes()
    rows=list(csv.DictReader(data.decode().splitlines()))
    legacy={q['id'] for q in json.loads((ROOT/'configs/questions.json').read_text()) if q['split']=='audit'}
    pool=[]
    for i,row in enumerate(rows):
        q={'id':f'mmlu_{i:04d}','question':row['question'],'options':ast.literal_eval(row['options']),
           'answer':row['answer'],'domain':row['domain']}
        q['split']='legacy_e01' if q['id'] in legacy else 'candidate'
        pool.append(q)
    candidates=[q for q in pool if q['split']=='candidate']
    rng=random.Random(cfg['question_seed']); rng.shuffle(candidates)
    dev=candidates[:cfg['instrument_development_questions']]
    for i,q in enumerate(dev):
        q['split']='instrument_dev'
        q['case_template']=cfg['templates'][i%2]
        q['case_mapping']=cfg['mappings'][(i//2)%2]
        q['tag_template']=cfg['templates'][(i+1)%2]
        q['tag_mapping']=cfg['mappings'][((i//2)+1)%2]
    for q in candidates[cfg['instrument_development_questions']:]: q['split']='confirmatory'
    output=sorted(pool,key=lambda q:q['id'])
    counts={s:sum(q['split']==s for q in output) for s in ('legacy_e01','instrument_dev','confirmatory')}
    assert counts=={'legacy_e01':12,'instrument_dev':48,'confirmatory':240},counts
    manifest={'source_commit':'5d78aeffe0152ba087c2d31cd07712d029c64785',
              'source_sha256':hashlib.sha256(data).hexdigest(),'counts':counts,'questions':output}
    (ROOT/'configs/e01r_questions.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(counts))

if __name__=='__main__': main()
