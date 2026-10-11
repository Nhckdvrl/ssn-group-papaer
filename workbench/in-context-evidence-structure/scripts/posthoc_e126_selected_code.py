"""POST-HOC E126 output diagnosis; never runs models or alters frozen primaries.

Opposite-convention worlds distinguish the selected other-source word's
agreement with that source's demonstrated rule from agreement with the
requested source's canonical code index rendered in the other word set.
"""
import json
from pathlib import Path
import numpy as np
from e118_criterion_code_feature_crossing import interval
ROOT=Path(__file__).resolve().parents[1]
def main():
    result={'status':'POST-HOC, after E126 full confirmation','unit':'context; origin-only, equal actors and queries',
        'scope':'Compatibility of observed output with private gold; does not identify an internal called rule.', 'runs':{}}
    report=['# E126 POST-HOC：另一Source的输出词携带哪套私人约定？','',
        '这是看到E126完整结果后新增的观察，不改冻结primary、不新增GPU。仅origin（相反private约定）可区分两规则；cross相同约定不用于此分解。所有context包含，不按是否犯错筛种子。逐查询直接用实际argmax token、词ID、两来源gold判断输出是否符合另一Source的演示规则；“请求code用另一词集写出”仅为构造任务的canonical index对照，不是词语天然语义。','',
        '| Model / phase | pair | other-source word, % | other word agreeing with its source rule, % | other word disagreeing with its source rule, % | own word wrong private code, % | outside both sets, % |','|---|---|---:|---:|---:|---:|---:|---:|']
    def f(v):return f"{100*v['mean']:.2f} [{100*v['ci95'][0]:.2f}, {100*v['ci95'][1]:.2f}]"
    for phase in ['discovery','confirmation']:
        for family in ['qwen3','mistral','llama']:
            d=ROOT/'results/e126'/f'{family}_{phase}'
            rows=[json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
            words=json.loads((d/'preflight.json').read_text())['word_ids']
            assert len(set(sum(words,[])))==4
            per={}
            for pair in ['00','11','01','10']:
                counts=[]
                for r in rows:
                    one={k:[] for k in ['other','other_rule','other_requested_index','own_bad_code','outside']}
                    for owner in [0,1]:
                        v=r['conditions'][f'origin_cache{pair}_joint_{owner}']
                        other_gold=r['conditions'][f'origin_cache{pair}_joint_{1-owner}']['gold']
                        for t,g,go in zip(v['argmax_token'],v['gold'],other_gold):
                            assert go==-g
                            in_other=t in words[1-owner];in_own=t in words[owner]
                            rule=in_other and t==words[1-owner][int(go>0)]
                            requested=in_other and t==words[1-owner][int(g>0)]
                            assert int(rule)+int(requested)==int(in_other)
                            for k,b in [('other',in_other),('other_rule',rule),('other_requested_index',requested),
                                        ('own_bad_code',in_own and t!=words[owner][int(g>0)]),('outside',not(in_own or in_other))]:one[k].append(b)
                    counts.append({k:np.mean(v) for k,v in one.items()})
                per[pair]={k:np.asarray([v[k] for v in counts]) for k in counts[0]}
                report.append('| '+family+' / '+phase+' | '+pair+' | '+' | '.join(f(interval(per[pair][k])) for k in per[pair])+' |')
            out={'pair_rates':{p:{k:interval(v) for k,v in values.items()} for p,values in per.items()},
                'coherent_minus_mixed':{k:interval(.5*(per['00'][k]+per['11'][k]-per['01'][k]-per['10'][k])) for k in per['00']}}
            result['runs'][family+'_'+phase]=out
    dest=ROOT/'results/e126'
    (dest/'posthoc_selected_code.json').write_text(json.dumps(result,indent=2)+'\n')
    (dest/'posthoc_selected_code.md').write_text('\n'.join(report)+'\n')
    print(json.dumps({k:v['coherent_minus_mixed'] for k,v in result['runs'].items() if k.endswith('confirmation')}))
if __name__=='__main__':main()
