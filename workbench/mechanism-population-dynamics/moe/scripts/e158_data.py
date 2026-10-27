"""E158 frozen factual inputs and label-only matched controls; CPU tokenizer only."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer, __version__ as transformers_version

WB=Path(__file__).resolve().parents[1]
READING=Path.home()/'mechpop_cache/moe_primary_reading_20261027/lre_official_1b9ec3cf'
RAW=Path.home()/'mechpop_cache/e158_factual_role_interchange'
PLAN=WB/'results/e158/data_plan.json'
COMMIT='1b9ec3cf2b8368e42bde7e80fcef384312a6ec07'
REV='d2a4949c9d4ad6cf47fbac131f7e020077332b21'
FILES={'country_capital_city.json':('9945d2da1fa1145c1d7e59ac61a25ebee74299c00bd53fc9308167f9e1d44fc0','b353e2a76acad8d370d97b46d66b776fcf6ec685'),
       'country_language.json':('0996525735107934f0d2e467e6fac7d2c785c42e8300ccb41ae6e9b5dfde2b76','a69180e3921b34e798688395c3ff45ca0cf0b768')}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def blob_sha(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def load_sources():
    manifest=json.loads((READING/'source_manifest.json').read_text())
    if manifest['commit']!=COMMIT:raise ValueError('LRE commit mismatch')
    entries={Path(x['path']).name:x for x in manifest['files']}
    records=[]
    for name,(sha256,blob) in FILES.items():
        path=READING/'data/factual'/name; data=path.read_bytes(); rec=entries[name]
        if rec['sha256']!=sha256 or rec['git_blob_sha1']!=blob or rec['bytes']!=len(data) or hashlib.sha256(data).hexdigest()!=sha256 or blob_sha(data)!=blob:
            raise ValueError('LRE source byte mismatch: '+name)
        records.append(json.loads(data))
    return records


def corrected_answers(rows):
    records=[]; out=[]
    for row in rows:
        value=row['object']
        if row['subject'] in ('Brazil','Colombia'):
            expected={'Brazil':r'Bras\u00edlia','Colombia':r'Bogot\u00e1'}[row['subject']]
            replacement={'Brazil':'Brasília','Colombia':'Bogotá'}[row['subject']]
            if value!=expected:raise ValueError('Unexpected literal escape')
            records.append({'subject':row['subject'],'source_object_literal':value,'corrected_object':replacement,
                            'reason':'Decode explicitly double-escaped Unicode from published JSON; original unchanged'})
            value=replacement
        elif '\\u' in value:raise ValueError('Unexpected escaped answer; do not silently change')
        out.append(value)
    if len(records)!=2:raise ValueError('Expected exactly two corrections')
    return out,records


def match_controls(source,target,rng):
    """Randomized augmenting-path bipartite perfect matching over source labels."""
    n=len(source)
    if len(target)!=n:raise ValueError('Bad matching dimensions')
    allowed=[rng.permutation([j for j in range(n) if source[j]!=source[i] and source[j]!=target[i]]).tolist() for i in range(n)]
    holder=[-1]*n
    def visit(i,seen):
        for j in allowed[i]:
            if j in seen:continue
            seen.add(j)
            if holder[j]<0 or visit(holder[j],seen):holder[j]=i;return True
        return False
    for i in rng.permutation(n):
        if not visit(int(i),set()):raise ValueError('No label-preserving control matching')
    result=np.empty(n,dtype=np.int64)
    for j,i in enumerate(holder):result[i]=source[j]
    if collections.Counter(result.tolist())!=collections.Counter(np.asarray(source).tolist()):raise AssertionError('control label frequencies differ')
    if np.any(result==source) or np.any(result==target):raise AssertionError('control shares target or source')
    return result


def get_tokenizer():
    meta=json.loads((WB/'results/e154/asset_manifest.json').read_text())['model']
    if meta['revision']!=REV:raise ValueError('P tokenizer revision mismatch')
    root=Path(meta['path'])
    for name in ('tokenizer.json','tokenizer_config.json','special_tokens_map.json'):
        rec=meta['files'][name];path=root/name
        if not path.is_file() or sha(path)!=rec['sha256']:raise ValueError('P tokenizer file mismatch: '+name)
    return AutoTokenizer.from_pretrained(root,local_files_only=True),meta


def build():
    (capital,language)=load_sources(); crows=capital['samples'];lrows=language['samples']
    if len(crows)!=24 or len(lrows)!=24:raise ValueError('Expected 24 subjects per relation')
    order=[x['subject'] for x in crows]; lookup={x['subject']:x for x in lrows}
    if len(set(order))!=24 or len(lookup)!=24 or set(order)!=set(lookup):raise ValueError('Countries not aligned')
    answers,corrections=corrected_answers(crows)
    all_answers=[answers,[lookup[x]['object'] for x in order]]
    templates=[[capital['prompt_templates'][1],capital['prompt_templates'][0]],
               [language['prompt_templates'][1],language['prompt_templates'][2]]]
    if any(not t.endswith(' is') for row in templates for t in row):raise ValueError('Expected is-ending templates')
    tokenizer,meta=get_tokenizer(); queries=[]; flat=[];offsets=[0]
    gold=np.zeros(96,np.int64); rel=np.zeros(96,np.int8); country=np.zeros(96,np.int8); template=np.zeros(96,np.int8)
    for r in range(2):
        for t in range(2):
            for c,subject in enumerate(order):
                qid=(r*2+t)*24+c; prompt=templates[r][t].format(subject);answer=all_answers[r][c]
                ids=tokenizer.encode(prompt,add_special_tokens=False)
                joined=tokenizer.encode(prompt+' '+answer,add_special_tokens=False)
                if not ids or len(joined)<=len(ids) or joined[:len(ids)]!=ids:raise ValueError(f'Prompt/answer boundary not prefix-preserving: {qid}')
                target=joined[len(ids)]; flat.extend(ids); offsets.append(len(flat));gold[qid]=target;rel[qid]=r;country[qid]=c;template[qid]=t
                queries.append({'qid':qid,'relation':r,'relation_name':('country_capital_city','country_language')[r],
                    'template':t,'country':c,'subject':subject,'prompt':prompt,'answer':answer,
                    'input_ids':ids,'answer_token_ids':joined[len(ids):],'gold_token':target})
    if len(set(q['input_ids'][-1] for q in queries))!=1:raise ValueError('Final prompt token differs')
    target=np.array([[r*48+c for c in range(24)] for r in range(2)],dtype=np.int64)
    sources=np.array([[[r*48+(c+11)%24 for c in range(24)] for r in range(2)],
                      [[(1-r)*48+c for c in range(24)] for r in range(2)],
                      [[r*48+24+c for c in range(24)] for r in range(2)]],dtype=np.int64)
    if not np.array_equal(gold[sources[2]],gold[target]):raise ValueError('Paraphrase gold token differs')
    if np.any(gold[sources[:2]]==gold[target][None,:,:]):raise ValueError('Entity/attribute source token equals target')
    rng=np.random.default_rng(158003);control=np.empty((3,2,24),np.int64)
    for scenario in range(3):
        for r in range(2):control[scenario,r]=match_controls(gold[sources[scenario,r]],gold[target[r]],rng)
    ranges=[np.unique(gold[target[r]]) for r in range(2)]
    range_ids=np.full((2,24),-1,np.int64);counts=np.array([len(v) for v in ranges],np.int64)
    for r,values in enumerate(ranges):range_ids[r,:len(values)]=values
    arrays={'ids':np.array(flat,np.uint32),'offsets':np.array(offsets,np.int64),'gold_token':gold,
            'relation':rel,'country':country,'template':template,'target_query_index':target,'source_query_index':sources,
            'control_token':control,'range_token_ids':range_ids,'range_count':counts,'token_union':np.unique(gold),
            'native_query_order':np.arange(96,dtype=np.int64)}
    return arrays,queries,corrections,templates,meta


def self_test():
    r=load_sources(); answers,fix=corrected_answers(r[0]['samples']);assert len(fix)==2 and 'Brasília' in answers and 'Bogotá' in answers
    src=np.array([0,0,1,1,2,2]);tar=np.array([1,1,2,2,0,0]);rng=np.random.default_rng(158003)
    a=match_controls(src,tar,rng);b=match_controls(src,tar,np.random.default_rng(158003));assert np.array_equal(a,b)
    arrays,queries,_,_,_=build();target=arrays['target_query_index'];s=arrays['source_query_index'];g=arrays['gold_token']
    for rel in range(2):
        for c in range(24):
            assert target[rel,c]==rel*48+c and s[0,rel,c]==rel*48+(c+11)%24 and s[1,rel,c]==(1-rel)*48+c and s[2,rel,c]==rel*48+24+c
    assert np.all(g[s[:2]]!=g[target][None,:,:]) and np.array_equal(g[s[2]],g[target])
    assert len({q['input_ids'][-1] for q in queries})==1 and arrays['offsets'][-1]==len(arrays['ids'])
    return {'status':'passed','CPU_only':True,'queries':len(queries),'matched_controls':144,'prefix_and_final_token_checks':True,'corrections':len(fix)}


def prepare():
    arrays,queries,corrections,templates,meta=build()
    RAW.mkdir(parents=True,exist_ok=True);PLAN.parent.mkdir(parents=True,exist_ok=True)
    payloads={'queries.json':{'queries':queries},'corrections.json':{'corrections':corrections}}
    for name,payload in payloads.items():
        path=RAW/name; text=json.dumps(payload,ensure_ascii=False,indent=2)+'\n'
        if path.exists() and path.read_text()!=text:raise ValueError('Refusing to overwrite changed '+str(path))
        if not path.exists():path.write_text(text)
    path=RAW/'data.npz'
    if path.exists():
        with np.load(path,allow_pickle=False) as old:
            if set(old.files)!=set(arrays) or any(not np.array_equal(old[k],v) for k,v in arrays.items()):raise ValueError('Refusing to overwrite changed '+str(path))
    else:np.savez_compressed(path,**arrays)
    paths={name:{'path':str(RAW/name),'sha256':sha(RAW/name),'bytes':(RAW/name).stat().st_size} for name in ('data.npz','queries.json','corrections.json')}
    plan={'experiment':'E158','status':'prepared','data_script_sha256':sha(Path(__file__)),'source_commit':COMMIT,
          'source_manifest':{'path':str(READING/'source_manifest.json'),'sha256':sha(READING/'source_manifest.json')},
          'source_files':{k:{'sha256':v[0],'git_blob_sha1':v[1]} for k,v in FILES.items()},
          'tokenizer':{'model':meta['repo_id'],'revision':REV,'path':meta['path'],'transformers_version':transformers_version,
                       'files':{k:meta['files'][k]['sha256'] for k in ('tokenizer.json','tokenizer_config.json','special_tokens_map.json')},
                       'add_special_tokens':False,'answer':'first token after exact prompt prefix'},
          'templates':templates,'labels':['country_capital_city','country_language'],'scenarios':['entity','attribute','paraphrase'],
          'matching':'seed158003 randomized augmenting path; source-label multiset permutation; excludes source and target tokens',
          'query_order':'qid=(relation*2+template)*24+country; qid r*48+c canonical',
          'last_prompt_token':queries[0]['input_ids'][-1],'num_queries':96,'range_count':arrays['range_count'].tolist(),
          'arrays':{k:{'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in arrays.items()},'assets':paths,
          'scope':'published labels only; no model output, training, GPU or test-set selection'}
    text=json.dumps(plan,ensure_ascii=False,indent=2)+'\n'
    if PLAN.exists() and PLAN.read_text()!=text:raise ValueError('Refusing to overwrite changed '+str(PLAN))
    if not PLAN.exists():PLAN.write_text(text)
    return {'status':'prepared','plan':str(PLAN),'queries':96,'range_count':arrays['range_count'].tolist()}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('self-test','prepare'));args=p.parse_args()
    print(json.dumps(self_test() if args.mode=='self-test' else prepare(),ensure_ascii=False,indent=2))
