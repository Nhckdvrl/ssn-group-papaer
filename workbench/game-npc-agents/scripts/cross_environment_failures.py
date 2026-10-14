#!/usr/bin/env python3
"""Read existing NPC evidence together; no new simulation or model calls."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=Path('/home/xiang/.cache/game-npc-research/runs')

def read(name):return json.loads((ROOT/'results'/name).read_text())

def main():
    light=read('E14_light_native_summary.json')
    report={'analysis':'POST-HOC cross-environment contradiction inventory, not a pooled benchmark',
            'new_model_calls':0,'new_engine_steps':0,'paid_cash_calls':0,
            'light_E14':{'episodes':len(light),'distinct_source_quests':len({r['npc_quest_file'] for r in light}),
                'goal_event_executed':sum(r['native_goal_event_executed'] for r in light),
                'goal_kinds':dict(Counter(r['npc_goal'].split()[0] for r in light)),
                'npc_legal':sum(r['npc_legal'] for r in light),'npc_actions':sum(r['turns'] for r in light),
                'persona_counterfactual':False,'task_binding_visible':True,
                'scope':'authored goal-following capability; not a causal persona-effect sample'},
            'light_E22':{},'E42':{},'campus_E49':[]}
    e22=read('E22_access_belief_summary.json')
    snapshots=json.loads((CACHE/'e22_qwen35/snapshots.json').read_text())
    for s in snapshots:
        r=e22[s['name']]
        interactions={c:s['contexts'][c].split('Recent visible interaction:\n',1)[1].split('Legal commands:',1)[0]
                      for c in ['partner_only','all_dialog']}
        report['light_E22'][s['name']]={'goal':s['quest']['goal'],
            'motivations':{k:s['quest'][k] for k in ['short_motivation','mid_motivation','long_motivation']},
            'conditions':r['conditions'],'visible_dialogue':interactions,
            'independent_scenes':1,'draws_per_cell':32,'persona_counterfactual':False,
            'physical_state_fixed':True,'all_cases_selected_before_this_analysis':True}
    e42=read('E42_all_240_native_episodes.json')
    for name,c in e42['conditions'].items():
        first=[]
        with (Path(c['raw'])/'model_calls.jsonl').open() as f:
            for line in f:
                r=json.loads(line)
                if r['cycle']!=0:break
                first.append(r)
        idx={(r['id'],r['world_seed'],r['input_C']):r for r in first}
        matches=[]
        for pid,w in sorted({(r['id'],r['world_seed']) for r in first}):
            h,l=idx[(pid,w,'high')],idx[(pid,w,'low')]
            ch=h['messages'][1]['content'].split('\n',1)[1]
            cl=l['messages'][1]['content'].split('\n',1)[1]
            matches.append({'id':pid,'world_seed':w,'high_action':h['executed_action'],
                            'low_action':l['executed_action'],'state_and_nonpersona_text_equal':ch==cl})
        report['E42'][name]={'model':c['model'],'prompt':c['prompt'],'peer_policy':c['peer_policy'],
            'episodes':c['episode_count'],'calls':c['calls'],'raw':c['raw'],
            'first_decision_pairs':matches,'first_action_differences':sum(r['high_action']!=r['low_action'] for r in matches),
            'whole_episode_four_cells':c['four_cells'],'class_counts':dict(Counter(x['descriptive_class'] for x in c['four_cells'])),
            'mean_four_cells':{k:sum(x[k] for x in c['four_cells'])/len(c['four_cells'])
                               for k in ['J_high_given_high','J_high_given_low','J_low_given_high','J_low_given_low','DD']},
            'speaker_dialogue_present':False,'explicit_preference_cue_changes_information':c['prompt']=='preference_cue',
            'cue_identical_between_C_levels':c['prompt']=='preference_cue',
            'DD_definition':'difference in differences, not a persona label',
            'architecture':'focal LLM, 15 frozen MLP peers; original Mini-Inzoi hand-written rewards'}
    campus=read('E49_complete_cross_role_commitments.json')
    for name,r in campus['branches'].items():
        s=r['summary'];actor=s['actor'];segments=r['actor_activity_segments'][actor]
        suffix=[x for x in segments if x['start']>=s['fork_step']]
        moves=[x for x in suffix if x['activity'].startswith('walking to ')]
        report['campus_E49'].append({'name':name,'actor':actor,'seed':s['seed'],
            'style':s['style'],'plan_channel':s['plan_channel'],'fork_step':s['fork_step'],
            'persona_scope':s['persona_intervention_scope'],'raw':r['raw'],
            'suffix_activity_segments':suffix,'first_suffix_walk':moves[0] if moves else None,
            'intentions':r['intention_extractions'],
            'lecture_sketch_completion_flag_available':False,
            'contrast_scope':'conversation-stage and agenda-input effects, not total persona effect'})
    report['source_files_sha256']={name:hashlib.sha256((ROOT/'results'/name).read_bytes()).hexdigest()
        for name in ['E14_light_native_summary.json','E22_access_belief_summary.json',
                     'E42_all_240_native_episodes.json','E49_complete_cross_role_commitments.json']}
    (ROOT/'results/CROSS_ENVIRONMENT_CONTRADICTIONS_2026-10-15.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'E14':report['light_E14'],'E42':{k:{'first_action_differences':v['first_action_differences'],
        'pairs':len(v['first_decision_pairs']),'classes':v['class_counts']} for k,v in report['E42'].items()},
        'campus_branches':len(report['campus_E49']),'new_model_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
