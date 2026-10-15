#!/usr/bin/env python3
"""Native state validation plus explicit indirect-ownership sensitivity, no model calls."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--runs',type=Path,nargs='+',required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();sources={r['case']['case_id']:r for r in map(json.loads,args.data.open())}
    cells=defaultdict(Counter); alternatives=[]; hashes={}; episodes=removes=gives=0
    for folder in args.runs:
        assert (folder/'runtime.json').exists()
        manifest=json.loads((folder/'manifest.json').read_text());model='gemma' if 'gemma' in manifest['model'].lower() else '32b'
        for r in map(json.loads,(folder/'episodes.jsonl').open()):
            episodes+=1;item=r['goal_item_id'];a=r['actor_id'];goal=r['goal_recipient_id']
            recipients=[]
            for h in r['history']:
                if not h['legal'] or not h.get('executed') or h.get('stochastic_failure'):continue
                if h['event_type']=='RemoveObjectEvent' and h['target_node_ids'][0]==item:
                    assert h['before'][item]['equipped'] and not h['after'][item]['equipped'];removes+=1
                if h['event_type']=='GiveObjectEvent' and h['target_node_ids'][0]==item:
                    target=h['target_node_ids'][1]
                    assert h['before'][item]['container']==a and h['after'][item]['container']==target
                    recipients.append(target);gives+=1
            assert len(recipients)<=1 and (recipients[0] if recipients else None)==r['first_recipient']
            source=sources[r['case_id']];graph=json.loads(source['states'][r['state']]);agents=set(graph['agents'])
            if r['history']:
                state=r['history'][-1]['after'];parent=lambda n:state.get(n,{}).get('container')
            else:
                nodes=graph['nodes'];parent=lambda n:(nodes.get(n,{}).get('container_node') or {}).get('target_id')
            node=item;seen=set()
            while node is not None and node not in agents:
                assert node not in seen;seen.add(node);node=parent(node)
            owner=node if node in agents else None
            cell=manifest['experiment']+'/'+model+'/'+r['persona']+'/'+r['condition']
            cells[cell].update(episodes=1,primary_to_goal=int(r['first_recipient']==goal),
                               terminal_indirect_owner_goal=int(owner==goal),
                               terminal_indirect_owner_competitor=int(owner==r['competitor_id']),
                               terminal_indirect_owner_actor=int(owner==a))
            if owner==goal and r['first_recipient']!=goal:
                alternatives.append({'experiment':manifest['experiment'],'model':model,'case_id':r['case_id'],
                                     'seed':r['seed'],'persona':r['persona'],'condition':r['condition'],
                                     'goal_item_id':item,'goal_recipient_id':goal,'terminal_owner':owner,
                                     'commands':[h['command'] for h in r['history']]})
        hashes[str(folder/'episodes.jsonl')]=hashlib.sha256((folder/'episodes.jsonl').read_bytes()).hexdigest()
    result={'status':'PASS','episodes':episodes,'verified_source_removes':removes,'verified_source_gives':gives,
            'physical_flag_mismatches':0,'cells':dict(cells),'indirect_goal_ownership_without_direct_source_give':alternatives,
            'source_sha256':hashes,'model_calls':0,
            'scope':['Primary first source-item Give unchanged; terminal transitive ownership is a separate sensitivity readout.',
                     'Indirect possession is not full private utility and uses the same episode stopping/horizon.',
                     'This is internal state validation, not independent L3 scientific review.']}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print({k:result[k] for k in ['status','episodes','verified_source_removes','verified_source_gives','physical_flag_mismatches']})
    print({'indirect_alternatives':len(alternatives)})


if __name__=='__main__':main()
