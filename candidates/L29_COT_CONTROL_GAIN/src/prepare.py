"""Fetch pinned public assets; never imports model code or starts a GPU job."""
import ast, csv, hashlib, json, pathlib, random, urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODEL='allenai/Olmo-3.1-7B-RL-Zero-Math'

def get(url):
    with urllib.request.urlopen(url, timeout=120) as f: return f.read()

def main():
    refs=json.loads(get('https://huggingface.co/api/models/'+MODEL+'/refs'))
    selected={x['name']:x['targetCommit'] for x in refs['branches'] if x['name'] in ['step_0100','step_1400','step_2800']}
    manifest={'model_id':MODEL,'revisions':selected,'source_commit':'5d78aeffe0152ba087c2d31cd07712d029c64785'}
    (ROOT/'configs/models.json').write_text(json.dumps(manifest,indent=2)+'\n')
    data=get('https://raw.githubusercontent.com/YuehHanChen/CoTControl/'+manifest['source_commit']+'/CoT-Control-QA/datasets/mmlu_pro_mini_w_keyword.csv')
    rows=list(csv.DictReader(data.decode().splitlines())); pool=[]
    for i,r in enumerate(rows):
        kw=ast.literal_eval(r['valid_keywords'])
        if r['domain'] in ['Math','Physics','Chemistry'] and kw and kw[0].isascii() and kw[0].isalpha():
            pool.append({'id':f'mmlu_{i:04d}','question':r['question'],'options':ast.literal_eval(r['options']),'answer':r['answer'],'domain':r['domain'],'keyword':kw[0]})
    random.Random(290912).shuffle(pool)
    for i,r in enumerate(pool): r['split']='audit' if i<12 else 'pilot'
    (ROOT/'configs/questions.json').write_text(json.dumps(pool,indent=2)+'\n')
    manifest['data_sha256']=hashlib.sha256(data).hexdigest()
    jobs=[]
    for step,sha in selected.items():
        info=json.loads(get('https://huggingface.co/api/models/'+MODEL+'/revision/'+sha+'?blobs=true'))
        folder=pathlib.Path('/home/xiang/.cache/l29')/step; folder.mkdir(parents=True,exist_ok=True)
        manifest.setdefault('files',{})[step]=[]
        for f in info['siblings']:
            name=f['rfilename']
            if name.endswith(('.safetensors','.json','.txt')) and '/' not in name:
                manifest['files'][step].append(f); jobs.append((sha,name,folder,f.get('lfs',{}).get('sha256')))
    (ROOT/'configs/models.json').write_text(json.dumps(manifest,indent=2)+'\n')
    def download(job):
        sha,name,folder,expected=job; dst=folder/name
        if not dst.exists():
            tmp=dst.with_suffix(dst.suffix+'.part')
            with urllib.request.urlopen(f'https://huggingface.co/{MODEL}/resolve/{sha}/{name}',timeout=180) as src, tmp.open('wb') as out:
                while chunk:=src.read(8*1024*1024): out.write(chunk)
            tmp.rename(dst)
        if expected:
            digest=hashlib.file_digest(dst.open('rb'),'sha256').hexdigest()
            if digest!=expected: raise RuntimeError(f'Hash mismatch: {dst}')
        print('verified',dst,flush=True)
    with ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(download,jobs))
if __name__=='__main__': main()
