#!/usr/bin/env python3
"""CPU-only independent E85 input lineage and typed-native readback.

The frozen scheduler is replayed with recorded exact input-key answers, never
a model client. A separate pass reconstructs each recorded full pre-state and
executes the original native event directly (not the driver's apply/execute
helper), checking all graph fields, delivered messages and visible history.
Recorded state restoration here is an audit of the actual trace, not a rewrite
of the original execution or a claim that a legacy loader was faithful.
"""
import argparse
from collections import Counter
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import tempfile

import native_partner_performance as driver
from light_native_gate import load_event_modules
from light_npc_episodes import CACHE, ViewerHost, material_state
from native_cooperation_episodes import SPEECH, identity
from native_independent_goal_episodes import binding
from native_independent_goal_qualification import goal_event

WB = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def key(row):
    return tuple(row[k] for k in ['history_id','seed','panel','branch','control'])


def lines(path):
    return [json.loads(line) for line in Path(path).open() if line.strip()]


def faithful_recorded_graph(text, modules):
    """Restore recorded scalar attributes omitted by upstream deserialization."""
    graph = modules[0].from_json(text)
    before, after = json.loads(text), json.loads(graph.to_json())
    for nid, node in before['nodes'].items():
        for field, value in node.items():
            if value != after['nodes'][nid].get(field):
                assert value is None or isinstance(value, (str,int,float,bool)), (nid,field,value)
                graph.get_node(nid).set_prop(field,value)
    assert json.loads(graph.to_json()) == before
    return graph


def load(runs, calls_from):
    rows, origins, states, calls, duplicates, hashes, manifests = {},{},{},{},[],{},{}
    for folder in runs:
        manifest = json.loads((folder/'manifest.json').read_text())
        assert manifest['experiment']=='E85'
        manifests[str(folder)] = manifest
        hashes[str(folder/'manifest.json')] = sha(folder/'manifest.json')
        for name in ['episodes.jsonl','states.jsonl']:
            hashes[str(folder/name)] = sha(folder/name)
        localstates = {key(r):r for r in lines(folder/'states.jsonl')}
        localkeys = set()
        for row in lines(folder/'episodes.jsonl'):
            k=key(row)
            assert k not in localkeys
            localkeys.add(k)
            if k in rows:
                same = row==rows[k] and localstates[k]==states[k]
                duplicates.append({'key':list(k),'exact_episode_and_states':same,
                    'first_source':str(origins[k]),'duplicate_source':str(folder)})
                assert same, ('Nonexact duplicate; no implicit version selection',k)
            else:
                rows[k],origins[k],states[k]=row,folder,localstates[k]
        expected={(h,s,p,b,c) for h in manifest['history_ids'] for s in manifest['seeds']
                  for p,b,c in ([('primary',b,c) for b in driver.CONDITIONS for c in driver.CONTROLS]
                                + [('revision',b,'check') for b in ['continue','withdraw']])}
        assert localkeys==expected
    for folder in dict.fromkeys([*runs,*calls_from]):
        path=folder/'model_calls.jsonl'
        if not path.exists():
            continue
        hashes[str(path)]=sha(path)
        for rec in lines(path):
            assert rec['decision_key']==driver.input_key(rec)
            if rec['decision_key'] in calls:
                assert all(calls[rec['decision_key']][f]==rec[f] for f in ['messages','schema','seed','parsed'])
            calls[rec['decision_key']]=rec
    return rows,origins,states,calls,duplicates,hashes,manifests


class ExactRecordedClient:
    def __init__(self,calls):
        self.calls=calls
        self.requests=[]

    def batch(self,jobs):
        answers=[]
        for job in jobs:
            dk=driver.input_key(job)
            assert dk in self.calls, ('No recorded exact input; audit performs no inference',
                                      {k:job.get(k) for k in ['history_id','panel','branch','control','turn','stage']},dk)
            rec=self.calls[dk]
            assert all(job[f]==rec[f] for f in ['messages','schema','seed'])
            self.requests.append({'decision_key':dk,'stage':job['stage'],'turn':job['turn']})
            answers.append(copy.deepcopy(rec['parsed']))
        return answers


def scheduler_rebuild(rows,states,histories,calls):
    count=Counter()
    requests=[]
    modules=load_event_modules(CACHE/'sources/LIGHT')
    # Rebuild one history/seed at a time. Sampling inputs contain no batch index;
    # the exact input key, recorded parsed result and every output row are tested.
    for hid,seed in sorted({(k[0],k[1]) for k in rows}):
        with tempfile.TemporaryDirectory(prefix='e85_cpu_rebuild_',dir=CACHE/'runs') as temp:
            out=Path(temp)
            client=ExactRecordedClient(calls)
            number=driver.run_group([histories[hid]],[seed],client,modules,out)
            rebuilt={key(r):r for r in lines(out/'episodes.jsonl')}
            rebuiltstates={key(r):r for r in lines(out/'states.jsonl')}
            assert number==len(rebuilt)==8
            wanted={k for k in rows if k[:2]==(hid,seed)}
            assert set(rebuilt)==wanted
            for k in wanted:
                assert rebuilt[k]==rows[k], ('Frozen scheduler native/metadata row differs',k)
                assert rebuiltstates[k]==states[k], ('Frozen scheduler full graph/history differs',k)
            count['whole_eight_branch_schedules_exact']+=1
            count['episodes_and_all_metadata_exact']+=len(wanted)
            for request in client.requests:
                count['exact_'+request['stage']+'_model_inputs']+=1
            requests.extend(client.requests)
    count['unique_recorded_input_keys_used']=len({r['decision_key'] for r in requests})
    count['new_model_calls']=0
    return dict(count)


def independent_native_replay(rows,states,histories,modules):
    counts=Counter()
    byte_differences=[]
    for k,row in sorted(rows.items()):
        h=histories[row['history_id']]
        case=driver.mapped_case(h)
        actors=case['actor_ids']
        assert row['actor_ids']==actors
        saved=states[k]['states']
        allturns=row['interventions']+row['turns']
        assert len(saved)==len(allturns)+1
        assert saved[0]['phase']=='source_cut'
        order=[h['source_role_map'][label] for label in ['npc','player']]
        assert saved[0]['visible']==[h['pre_player_visible'][i] for i in order]
        # Compare the recorded starting graph to the original full source cut;
        # legacy normalization is reported, never silently called an exact cut.
        if json.loads(saved[0]['graph'])!=json.loads(h['pre_player_graph_json']):
            counts['episodes_with_nonexact_legacy_sourcecut']+=1
        assert [driver.header(case,i) for i in [0,1]]==[h['private_headers'][i] for i in order]
        counts['own_private_headers_checked']+=2
        for pos,t in enumerate(allturns):
            pre,after=saved[pos],saved[pos+1]
            graph=faithful_recorded_graph(pre['graph'],modules)
            host=ViewerHost(graph)
            assert material_state(graph)==t['before']
            i=t['index'];actor=graph.get_node(actors[i])
            assert t['actor']==actors[i] and t['turn']==after['turn']
            event_type,ids=t['event_identity']
            assert event_type==t['event_type']
            expected,why=goal_event(graph,binding(case,i),modules)
            assert (identity(expected) if expected else None)==t['original_goal_current_identity']
            assert why==t['original_goal_current_unavailable_reason']
            choice=t['choice']
            if t.get('model_decision'):
                if choice['tool']=='SAY':
                    assert event_type=='SayEvent' and ids==[]
                    payload=choice['utterance']
                else:
                    # Exact tool catalogue identity, rather than ambiguous name
                    # parsing, must reproduce the model's chosen native action.
                    menu=driver.catalogue(graph,actor)
                    chosen=menu[choice['tool']]
                    assert identity(chosen)==t['event_identity']
                    payload=choice['utterance'] if event_type in SPEECH else chosen.text_content
            else:
                payload=choice['utterance'] if event_type in SPEECH else ''
            cls=getattr(modules[1],event_type)
            native=cls.construct_from_args(actor,[graph.get_node(n) for n in ids],payload)
            assert identity(native)==t['event_identity']
            if sha_text(graph.to_json())!=t['graph_before_sha256']:
                byte_differences.append({'key':list(k),'turn':t['turn'],'phase':t.get('phase')})
            random.seed(row['seed']+int(row['case_id'][:7],16)*100+t['turn']+1000)
            if isinstance(native,modules[2]):
                assert not t['legal'] and not t['executed'] and native.view_as(actor)==t['error']
            else:
                assert t['legal']
                try:
                    native.execute(host)
                    assert bool(native.executed)==t['executed']
                    assert bool(getattr(native,'failed',False))==bool(t.get('stochastic_failure'))
                except Exception as exc:
                    assert type(exc).__name__+': '+str(exc)==t.get('native_exception')
            assert host.messages==t['messages'], ('Actual delivered native messages differ',k,t['turn'])
            assert material_state(graph)==t['after']
            assert json.loads(graph.to_json())==json.loads(after['graph']), ('Full native post-state differs',k,t['turn'])
            visible=copy.deepcopy(pre['visible'])
            for index,aid in enumerate(actors):
                seen=[m['text'] for m in host.messages if m['viewer']==aid]
                if index==i:
                    seen.insert(0,'Your actual tool attempt: '+t['command'])
                    if t.get('native_exception'):seen.append('Native error: '+t['native_exception'])
                    elif t.get('error'):seen.append('Native rejection: '+t['error'])
                    elif not t.get('executed'):seen.append('Native tool did not record execution.')
                visible[index].extend(seen)
            assert visible==after['visible'], ('Actual per-role history differs',k,t['turn'])
            counts['original_typed_native_events_independently_replayed']+=1
            counts['full_graph_and_delivered_history_transitions_checked']+=1
            if t.get('model_decision') and event_type not in SPEECH and choice.get('utterance'):
                counts['non_speech_extra_payloads_not_delivered']+=1
        assert material_state(faithful_recorded_graph(saved[-1]['graph'],modules))==row['final_state']
        if row['panel']=='revision':
            parent=rows[(row['history_id'],row['seed'],'primary','real_claim','check')]
            first=next(t for t in parent['turns'] if t['turn']==0)
            assert row['turns'][0]==first
            assert row['turns'][1]['event_type']=='SayEvent' and row['turns'][1]['index']==1
            assert not row['turns'][1]['model_decision']
            counts['revision_exact_parent_first_action_checked']+=1
        counts['whole_native_sequences_checked']+=1
        counts['sourcecut_full_graph_snapshots_checked']+=1
    return {'status':'PASS',**dict(counts),'before_graph_byte_sha_differences':byte_differences}


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runs',type=Path,nargs='+',required=True)
    ap.add_argument('--calls-from',type=Path,nargs='*',default=[])
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--compatibility-wrapper',type=Path)
    a=ap.parse_args()
    rows,origins,states,calls,dups,hashes,manifests=load(a.runs,a.calls_from)
    datasets={m['data'] for m in manifests.values()}
    assert len(datasets)==1
    data=Path(next(iter(datasets)))
    histories={h['history_id']:h for h in driver.load_histories(data)}
    hashes[str(data)]=sha(data)
    wrapper=None
    if a.compatibility_wrapper:
        spec=importlib.util.spec_from_file_location('e85_compatibility_audit',a.compatibility_wrapper)
        wrapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(wrapper)
        # The wrapper must explicitly expose its audited install entry point.
        wrapper.install()
        hashes[str(a.compatibility_wrapper)]=sha(a.compatibility_wrapper)
    rebuilt=scheduler_rebuild(rows,states,histories,calls)
    native=independent_native_replay(rows,states,histories,load_event_modules(CACHE/'sources/LIGHT'))
    result={'experiment':'E85','status':'PASS','scope':'Independent CPU replay of actual saved records; no model/API/GPU calls.',
        'episodes':len(rows),'histories':len({r['history_id'] for r in rows.values()}),
        'original_graphs':len({r['graph_sha256'] for r in rows.values()}),
        'exact_input_scheduler_rebuild':rebuilt,'independent_original_native_replay':native,
        'exact_profile_duplicates':dups,'source_sha256':hashes,
        'rebuild_script':str(Path(__file__).resolve()),'rebuild_script_sha256':sha(__file__),
        'compatibility_wrapper':str(a.compatibility_wrapper) if wrapper else None,
        'new_model_calls':0,'new_API_calls':0,'new_GPU_jobs':0}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','episodes','histories','original_graphs','exact_input_scheduler_rebuild','independent_original_native_replay']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
