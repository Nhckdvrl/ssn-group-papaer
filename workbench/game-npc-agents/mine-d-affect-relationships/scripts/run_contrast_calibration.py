#!/usr/bin/env python3
"""Run and aggregate the preregistered D-E13 readout calibration, locally."""
import argparse
from collections import defaultdict
import datetime
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from run_adaptation_pipeline import Q32,read,write


def parse(text,body):
    text=text.strip();fenced=text.startswith('```')
    if fenced:text=text.split('\n',1)[-1].rsplit('```',1)[0].strip()
    try:v,end=json.JSONDecoder().raw_decode(text)
    except (ValueError,TypeError):return None
    if not isinstance(v,dict) or type(v.get('observable_contrast')) is not bool:return None
    if v.get('mapping') not in ['A1_B2','A2_B1','underdetermined'] or not isinstance(v.get('quotes'),list):return None
    quoted=set();supported=True
    for q in v['quotes']:
        if not isinstance(q,dict) or type(q.get('response')) is not int or q['response'] not in [1,2] or not isinstance(q.get('quote'),str):return None
        snippet=' '.join(q['quote'].split());candidate=' '.join(body['response_'+str(q['response'])].split())
        supported &= len(snippet)>=8 and snippet in candidate;quoted.add(q['response'])
    if v['mapping']!='underdetermined':supported &= quoted=={1,2}
    return dict(v,quotes_supported=bool(supported),strict_json=not fenced and not text[end:].strip())


def main():
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--sync-main',action='store_true');a=p.parse_args()
    root=Path(a.asset_root);data=root/'data/contrast_D-E13';out=root/'runs/D-E13';out.mkdir(exist_ok=False)
    status=dict(complete=False,error=None,phase='waiting_for_idle_gpu',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        status['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'finish_status.json').write_text(json.dumps(status,indent=2)+'\n')
    save();(out/'coordinator_source.py').write_bytes(Path(__file__).read_bytes());start=None
    try:
        manifest=json.loads((data/'manifest.json').read_text());tasks=read(data/'tasks.jsonl')
        if hashlib.sha256((data/'tasks.jsonl').read_bytes()).hexdigest()!=manifest['task_sha256']:raise ValueError('Frozen tasks changed')
        gpu=os.environ.get('CUDA_VISIBLE_DEVICES','0').split(',')[0]
        while int(subprocess.check_output(['nvidia-smi','--id='+gpu,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())>=1024:time.sleep(30)
        start=time.monotonic();status['phase']='judge';save()
        def invoke(file,name,cap):
            remaining=5400-(time.monotonic()-start)
            if remaining<=0:raise TimeoutError('Registered calibration budget exhausted')
            cmd=[sys.executable,str(Path(__file__).with_name('run_local_text.py')),'--tasks',str(file),'--checkpoint',Q32,
                '--revision',Path(Q32).name,'--model','qwen3_32b_calibration_judge','--out',str(out/name),
                '--batch-size','2','--max-tokens',str(cap),'--max-seconds',str(remaining)]
            with (root/'logs'/('D-E13-'+name+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
            return {r['task_id']:r for r in read(out/name/'responses.jsonl')}
        first=invoke(data/'tasks.jsonl','first',512)
        bad=[t for t in tasks if parse(first[t['task_id']]['response'],json.loads(t['messages'][1]['content'])) is None];second={}
        if bad:
            write(out/'recovery_tasks.jsonl',bad);second=invoke(out/'recovery_tasks.jsonl','recovery',1024)
        selected=[]
        for t in tasks:
            r=second.get(t['task_id'],first[t['task_id']]);v=parse(r['response'],json.loads(t['messages'][1]['content']))
            score=None if t['expected_mapping'] is None or v is None else .5 if v['mapping']=='underdetermined' else int(v['mapping']==t['expected_mapping'])
            selected.append(dict(**{k:t[k] for k in ['task_id','probe_id','novel','material','orientation','stratum','expected_mapping']},
                valid=v is not None,result=v,source_pairing_score=score,selected_attempt=2 if t['task_id'] in second else 1))
        write(out/'selected.jsonl',selected)
        import numpy as np
        books=sorted({t['novel'] for t in tasks});draws=np.random.default_rng(173).integers(0,len(books),(10000,len(books)))
        result=dict(experiment='D-E13',status='CALIBRATION-COMPLETE-NOT-EXPERIENCE-INTERVENTION',manifest=manifest,
            judgment_attempts=len(first)+len(second),actor_generation_calls=0,gpu_process_hours=(time.monotonic()-start)/3600,
            groups={},causal_experience_claim=False,
            interpretation='Source-state matching combines behavioral distinguishability with expected direction. Low/reversed matching is not proof of insensitivity. Identical controls test forced guessing, not real-world scope invariance. All data are previously observed phase controls.')
        for material in sorted({t['material'] for t in tasks}):
            rows=[r for r in selected if r['material']==material];valid=[r for r in rows if r['valid']]
            primary=[r for r in rows if r['stratum']!='overlap_or_expression'];pairs=defaultdict(list)
            for r in rows:pairs[r['probe_id']].append(r)
            consistency=[]
            for pair in pairs.values():
                if len(pair)==2 and all(r['valid'] for r in pair):
                    x,y=[r['result']['mapping'] for r in pair]
                    consistency.append((x==y=='underdetermined') or {x,y}=={'A1_B2','A2_B1'})
            stats=dict(valid=len(valid),planned=len(rows),observable_contrast_rate=statistics.mean(r['result']['observable_contrast'] for r in valid) if valid else None,
                underdetermined_rate=statistics.mean(r['result']['mapping']=='underdetermined' for r in valid) if valid else None,
                quote_supported_rate=statistics.mean(r['result']['quotes_supported'] for r in valid) if valid else None,
                swap_consistency=statistics.mean(consistency) if consistency else None,primary_by_book={},primary_macro=None)
            decisive=[r for r in valid if r['result']['mapping']!='underdetermined']
            stats['decisive_quote_supported_rate']=statistics.mean(r['result']['quotes_supported'] for r in decisive) if decisive else None
            if material!='identical_reference':
                for book in books:
                    values=[r['source_pairing_score'] for r in primary if r['novel']==book]
                    stats['primary_by_book'][book]=statistics.mean(values) if values and all(x is not None for x in values) else None
                if all(v is not None for v in stats['primary_by_book'].values()):
                    vals=np.array([stats['primary_by_book'][b] for b in books]);stats['primary_macro']=float(vals.mean());stats['primary_ci95']=np.quantile(vals[draws].mean(1),[.025,.975]).tolist()
                stats['by_stratum']={s:dict(n_pairs=len({r['probe_id'] for r in rows if r['stratum']==s}),
                    mean=statistics.mean(r['source_pairing_score'] for r in rows if r['stratum']==s) if all(r['valid'] for r in rows if r['stratum']==s) else None) for s in ['decision','strategy','overlap_or_expression']}
            result['groups'][material]=stats
        result['pairs']=[{k:v for k,v in r.items() if k!='result'}|dict(mapping=r['result']['mapping'] if r['valid'] else None,
            observable_contrast=r['result']['observable_contrast'] if r['valid'] else None,quotes_supported=r['result']['quotes_supported'] if r['valid'] else None) for r in selected]
        destination=Path(__file__).resolve().parent.parent/'results';(destination/'D-E13-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        lines=['# D-E13：行为对照读数校准','','**此项没有改变经历，不能作为经历因果效应或成长能力的结果。**',
            f"25候选probe中{manifest['n_probes']}对具备实际状态输入，{len(manifest['source_exclusions'])}对有来源资格缺失。分层{manifest['strata']}；主要行为读数{manifest['n_primary_behavior_probes']}对。六作品等权，换序不当独立样本。",'',
            '| 材料 | 有效判别 | 主要来源配对分数 | 95%作品区间 | 无法区分率（所有合格对） | 换序一致率 |',
            '|---|---:|---:|---|---:|---:|']
        for name,s in result['groups'].items():lines.append(f"| {name} | {s['valid']}/{s['planned']} | {s['primary_macro']} | {s.get('primary_ci95','不适用')} | {s['underdetermined_rate']} | {s['swap_consistency']} |")
        lines+=['','0.5表示随机对应的参照或无法区分的中性计分，不是作用域正确率。系统性配反可能含方向问题；仅凭此分数不能说模型未受输入影响。空对照两回复逐字相同，主要看是否承认无法区分。','',
            '所有实际演员回复来自既有真实运行；只新增本地判别调用。原文证据、初次/恢复回复和冻结输入留在ASSETS路径。此自动表仍需证据引用与语义审阅，不自动升级CLAIMS。']
        (destination/'D-E13-RUN-REPORT.md').write_text('\n'.join(lines)+'\n')
        if a.sync_main:
            repo=Path(__file__).resolve().parents[4];files=[str((destination/f).relative_to(repo)) for f in ['D-E13-summary.json','D-E13-RUN-REPORT.md']]
            if subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()!='main':raise RuntimeError('Branch changed; results saved')
            subprocess.run(['git','add','--',*files],cwd=repo,check=True)
            subprocess.run(['git','commit','--only','-m','保存行为配对仪器的实际校准，明确不构成经历因果结论','--',*files],cwd=repo,check=True)
            subprocess.run(['git','push','origin','main'],cwd=repo,check=True)
        status['complete']=True;status['phase']='saved_pending_semantic_review'
    except BaseException as e:
        status['error']=repr(e);raise
    finally:
        if start is not None:status['wall_s']=time.monotonic()-start
        save()


if __name__=='__main__':main()
