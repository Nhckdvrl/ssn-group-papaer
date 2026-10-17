#!/usr/bin/env python3
"""Bounded CPU evidence extraction after both complete E84 datasets. No labels/model calls."""
from collections import Counter
import hashlib
import json
from pathlib import Path

CACHE = Path('/home/xiang/.cache/game-npc-research/runs')
WB = Path(__file__).resolve().parents[1]
HERE = CACHE/'e84_independent_goal_readback'
SPEECH = {'SayEvent','TellEvent','WhisperEvent','ShoutEvent'}
MATERIAL = {'GiveObjectEvent','GetObjectEvent','StealObjectEvent','DropObjectEvent',
    'PutObjectInEvent','EatEvent','DrinkEvent','IngestEvent','WearEvent','WieldEvent',
    'EquipObjectEvent','RemoveObjectEvent'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def ok(t):return t['legal'] and t.get('executed') and not t.get('stochastic_failure')
def steps(r):return ([r['opening']] if r.get('opening') else [])+r['turns']

source = CACHE/'e84_native_qualification/cross_snapshots.jsonl'
cases = {r['case_id']:r for r in map(json.loads,source.open())}
rows, provenance, coverage, summaries = {}, {}, [], {}
for model in ['gemma','32b']:
    raw = CACHE/f'e84_{model}_full/episodes.jsonl'
    audit = WB/f'results/E84_{model}_complete_audit.json'
    reviewed = json.loads(audit.read_text())
    assert reviewed['independent_full_state_and_input_audit']['status']=='PASS'
    rr = list(map(json.loads,raw.open()))
    assert len(rr)==64 and len({(r['case_id'],r['seed']) for r in rr})==64
    provenance[str(raw)]={'sha256':sha(raw),'rows':len(rr)}
    provenance[str(audit)]={'sha256':sha(audit),'status':'PASS'}
    counts = Counter(); different_assets=[]; same_asset_only=[]
    for r in sorted(rr,key=lambda r:(r['case_id'],r['seed'])):
        cid,s = r['case_id'],r['seed'];c=cases[cid]
        rows[model,cid,s]=r
        actions=[];give=[set(),set()]
        failed=Counter();speech=Counter();unsent=0
        for t in steps(r):
            event,ids=t['event_identity']
            if t.get('stochastic_failure'):failed[event]+=1
            if ok(t) and event in SPEECH:speech[str(t['index'])]+=1
            if event not in SPEECH and t['choice'].get('utterance'):unsent+=1
            if ok(t) and event in MATERIAL:
                item=ids[0]
                actions.append({'turn':t['turn'],'actor_id':t['actor'],'index':t['index'],
                    'event':event,'target_ids':ids,'before':t['before'].get(item),'after':t['after'].get(item)})
                counts['successful_'+event]+=1
                if event=='GiveObjectEvent' and ids[1]==c['actor_ids'][1-t['index']]:
                    give[t['index']].add(item)
        opposite=bool(give[0] and give[1])
        distinct=any(a!=b for a in give[0] for b in give[1])
        if distinct:different_assets.append([cid,s])
        elif opposite:same_asset_only.append([cid,s])
        counts['episodes_any_successful_material_action']+=bool(actions)
        counts['episodes_any_Give']+=any(a['event']=='GiveObjectEvent' for a in actions)
        counts['episodes_opposite_Give_different_assets']+=distinct
        counts['episodes_opposite_Give_same_asset_only']+=opposite and not distinct
        counts['non_speech_payloads_not_transmitted']+=unsent
        for e,n in failed.items():counts['native_failed_flag_'+e]+=n
        coverage.append({'model':model,'case_id':cid,'seed':s,'graph_sha256':r['graph_sha256'],
            'quest_files':r['quest_files'],'raw_episode_path':str(raw),'raw_episode_canonical_sha256':canonical(r),
            'goal_verbs':[b['verb'] for b in c['goal_bindings']],
            'strict_events_ever':r['strict_goal_ever'],'physical_initial':r['physical_goal_initial'],
            'physical_ever':r['physical_goal_ever'],'physical_final':r['physical_goal_now'],
            'successful_native_material_actions':actions,'actual_speech_event_counts':dict(speech),
            'native_failed_flags_by_event':dict(failed),'native_errors':[{'turn':t['turn'],
                'error':t.get('error'),'exception':t.get('native_exception')} for t in steps(r)
                if t.get('error') or t.get('native_exception')],
            'opposite_Give_different_assets':distinct,'opposite_Give_same_asset_only':opposite and not distinct,
            'final_health':r['final_health'],'final_dead':r['final_dead'],'stop':r['stop']})
    summaries[model]={'logical_episodes':len(rr),'source_pairs':len({r['case_id'] for r in rr}),
        'original_graphs':len({r['graph_sha256'] for r in rr}),'objective_counts':dict(counts),
        'opposite_Give_different_asset_episode_keys':different_assets,
        'opposite_Give_same_asset_only_episode_keys':same_asset_only}

index=HERE/'E84_all_cohort_native_material_flow_index_POST_HOC.jsonl'
index.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in coverage))

def one(model,cid,seed,turns):
    r=rows[model,cid,seed];c=cases[cid];actual=[]
    byturn={t['turn']:t for t in steps(r)}
    for turn in turns:
        t=byturn[turn];event,ids=t['event_identity']
        touched=set(ids)|set(c['actor_ids'])|{b['item_id'] for b in c['goal_bindings'] if b.get('item_id')}
        delta={}
        for n in sorted(touched):
            before,after=t['before'].get(n),t['after'].get(n)
            if before==after:continue
            if before is None or after is None:delta[n]={'before':before,'after':after};continue
            delta[n]={f:{'before':before.get(f),'after':after.get(f)} for f in sorted(set(before)|set(after)) if before.get(f)!=after.get(f)}
        e={'turn':turn,'actor_index':t['index'],'actor_id':t['actor'],'native_event':event,
            'target_ids':ids,'executed':t.get('executed'),
            'native_failed_flag':t.get('stochastic_failure',False),'material_delta':delta}
        if event in SPEECH and ok(t):
            peer=c['actor_ids'][1-t['index']]
            e['actual_native_messages_to_partner']=[m for m in t['messages'] if m['viewer']==peer]
        else:
            e['command']=t['command']
            if t['choice'].get('utterance'):e['extra_payload_not_transmitted_as_speech']=True
        actual.append(e)
    return {'model':model,'seed':seed,'raw_episode_path':str(CACHE/f'e84_{model}_full/episodes.jsonl'),
        'episode_canonical_sha256':canonical(r),'selected_actual_events':actual,
        'all_material_actions_index_key':[model,cid,seed],
        'strict_events_ever':r['strict_goal_ever'],'physical_initial':r['physical_goal_initial'],
        'physical_ever':r['physical_goal_ever'],'physical_final':r['physical_goal_now'],
        'goal_item_final_state':{b['item_id']:{k:v for k,v in r['final_state'].get(b['item_id'],{}).items() if k in ['container','equipped']}
            for b in c['goal_bindings'] if b.get('item_id')},
        'final_health':r['final_health'],'stop':r['stop']}

specs=[
('160742ded667ed21c3ba1c56','请求后真实提供食物，通过Drop而非Give实施',
 [('gemma',8402,[-1,10,11,13])],
 'visitor以饥饿/想吃Chocolate开启交流，friend实际Drop自己的Chocolate，visitor随后Get并Eat。这里确有对另一方原生消费目标的物理帮助，无需把Give作为唯一合作动作。',
 'friend的原Drop sleeping bag目标涉及本就在visitor手中的另一个物；未执行该原子事件不等于没有帮助。游客的精力/后续买礼物未因此全部证明完成，不称双赢交易。'),
('63e1c3c7db75553de0dba339','先前偷窃后明确拒借：保留人物自主选择',
 [('gemma',8402,[10,16,17,27])],
 'friend偷睡袋失败后，提出交出自己的Chocolate换借睡袋一晚。visitor实际说不愿借出，明确联系到此前偷窃，并转谈纪念品；睡袋保持visitor持有。拒绝是真实互动结果，不能由未达双方goal自动判为不会合作。',
 '这是一条观察轨迹，没有把先前偷窃随机操纵成反事实；不能从此单例估计信任因果效应或宣称拒绝最优。'),
('c22bb96e1d30526d715cc3e4','同一原任务中的条件借用落实、拒绝及取消',
 [('32b',8401,[3,6,12,13,16,17,18,20,21,22]),
  ('gemma',8401,[3,4,5,6,7,8,13]),('gemma',8402,[3,4,5,7,8,19,21])],
 '32B先真正把hook交给fisherman，之后sailor请求借/买knife，fisherman同意有条件借用并要求航海后归还；sailor答应，fisherman实际Remove再Give，sailorWield。双方当前物资帮助确实发生，不能被原Steal和Put标签掩盖。Gemma8402则明确拒绝用自己的knife交易/出借；8401谈的是未绑定实际bait的对价，之后真实偷pouch失败、互Block，再口头取消knife交易。',
 '32B中间两次偷knife失败也完整保留。真实双资产流不是预先定价的hook换knife合同；航海后归还没有在本回合实现的deadline/航海flag，不计逾期。fisherman原Put hook入pouch仍未完成。两模型同时更换两个角色的控制模型，seed/历史也不同，不能当NPC单方因果效应。'),
('b304ce412e4d9ecee4a4f197','物理上可行且曾获接受的方案，随后没有成交',
 [('gemma',8402,[1,2,3,4,5,6,10,11,12,31])],
 '此轨迹fisherman提出hook换knife，sailor口头接受，两个物品均真实存在且分别由两人持有。随后转入Follow/Block、偷pouch失败、道歉和离别，直到本回合结束都没有实际hook/knife交接。说明不能把所有未完成都归为从未形成可执行方案。',
 '不能忽略方案后的互动变化或直接称纯执行能力缺失。它与c22bb共享原图和人物资产，但fisherman原作者goal是Give hook给sailor，而非Put hook入pouch；不是同一作者任务的配对因果对照。t31的再次口头提供也不是物理交付。'),
('12c39f0380b4b524b35b1c58','一方真实交付、另一项约定服务缺少原生实现',
 [('gemma',8401,[3,4,5,7,8,11,23,31])],
 '双方谈定leech换短暂staff使用，doctor实际Give leech，之后仍讨论演示和归还；staff从未离开witch。原始目标所需的staff取得未实现，leech取得则已真实实现。',
 '约定原话是一次channel/use，未明确必须转移所有权；此引擎无相应channel/heal动作或治愈flag，因此不能把没有Give staff直接打成违约或断言已治好King。这一例说明应区分实物前提与仅叙事服务。'),
('19368d9aeeb3a5faf9371be0','既有帮助之后继续响应实际请求，并保留后续回转',
 [('32b',8402,[-1,4,5,16,17,18,20,21,22,24,25,27,29,31])],
 'camper提出fruit换princess的物品；book真实交付后fruit也真实提供并被吃下。随后camper表示愿意继续帮忙，公主明确请求herb，camper实际给药草、公主实际Ingest并致谢。这是伙伴先前所做之事与后续新请求相连的完整正向互动，不能仅报两个Steal标签。',
 '必须保留尾部：camper把book归还公主后又尝试偷回并最终成功。不能在首次达成时停表。初始/最终HP都为10，Ingest herb不等于已证明治愈；无法仅据这些动作判定全部更高目的或最优决策。')]

comparisons=[]
for cid,title,ee,reading,limit in specs:
    c=cases[cid]
    comparisons.append({'candidate_id':cid,'graph_sha256':c['graph_sha256'],'title':title,
        'source_roles':[{'actor_id':c['actor_ids'][i],'quest_file':q['source_file'],
            'goal':q['goal'],'short_motivation':q['short_motivation'],
            'mid_motivation':q['mid_motivation'],'long_motivation':q['long_motivation'],
            'bound_item_id':c['goal_bindings'][i].get('item_id')}
            for i,q in enumerate(c['quests'])],
        'episodes':[one(m,cid,s,tt) for m,s,tt in ee],
        'our_reading':reading,'scope_and_competing_explanations':limit})

out={'experiment':'E84','status':'POST_HOC_COMPLETE_COHORT_GROUNDED_PLAN_READBACK',
    'date':'2026-10-16','corresponding':'I04 / P12; no claim upgrade',
    'timing':'Selected after all completed native trajectories; qualitative illustrations, not preregistered labels/endpoints or another independent dataset.',
    'main_reading':['普通双角色系统已经能在原世界真实提供食物、通过Drop/Get帮助、取得物资后回应新请求，以及落实附带将来归还条件的借用。',
        '另有合法拒绝、取消方案、最初可行方案被后续行为打断；缺少两个原子goal不能统一解释为不会合作。',
        '原本已true的交付关系、仅原生事件identity未发生但实际物资已取得、以及需要引擎未实现服务的叙事目的必须区分。',
        '仍有真实难点：提出/接受的计划与后续物理操作不总一致，已经交付/返还的物品会进入回转或再夺取；本轮不把它预定为通用机制或按少数例子调提示。'],
    'coverage_index':{'path':str(index),'sha256':sha(index),'logical_episodes':len(coverage),
        'source_pairs':len({r['case_id'] for r in coverage}),'original_graphs':len({r['graph_sha256'] for r in coverage}),
        'models':summaries,'definition':'Every successful native material action across all 128 logical episodes; profile duplicates excluded. Opposite-direction Give of distinct assets is a flow fact, not economic exchange, agreement success or mutual utility. No complete-corpus semantic annotation.'},
    'source_snapshot':{'path':str(source),'sha256':sha(source)},'provenance':provenance,
    'comparisons':comparisons,
    'quotation_rule':'Only successful native speech events and their recorded actual viewer messages are quoted. Any utterance attached to a non-speech action is untransmitted metadata, never dialogue evidence.',
    'scope':['The two models control both characters. Case/model/seed contrasts here are descriptive, not an isolated NPC intervention.',
        'Full 32-pair/23-graph cohort and all failures remain; illustrations do not define a scenario filter or rates of plans/fulfillment.',
        'The E81-shared header already explicitly says only selected speech transmits text and non-speech utterance should be empty. Nevertheless Gemma has 612 non-speech extra payloads and Qwen has 10. Such text did not reach the partner and may change what each side actually knows and how negotiation proceeds. Model contrasts and unfulfilled plans cannot all be attributed to strategy or persona mechanisms; this readback starts no format-repair grid.',
        'Source same-graph quests were independently authored, not a jointly authored cooperation game. No private-utility or cooperation-success gold is introduced.',
        'Native event.failed is retained by event type; Reward failure from no XP is deterministic, not a random skill failure.'],
    'rebuild':{'script':str(Path(__file__).resolve()),'sha256':sha(__file__),
        'command':'python3 '+str(Path(__file__).resolve())},
    'new_model_calls':0,'new_API_calls':0,'new_GPU_hours':0}
dest=WB/'results/E84_grounded_plans_POST_HOC.json'
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'out':str(dest),'bytes':dest.stat().st_size,'comparisons':len(comparisons),
    'illustrative_episodes':sum(len(c['episodes']) for c in comparisons),
    'full_cohort_index':str(index),'rows':len(coverage),'sha256':sha(index)},ensure_ascii=False))
