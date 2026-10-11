"""E88 input-only early predicate / critical NP visibility locations."""
import argparse
import collections
import json
from pathlib import Path
from data import sha
from prequestion_oracle_map import aligned_span,normalized_words

# Finite surface inventory from the complete published GP sources, read before this pilot.
# It locates words, supplies no semantic gold and does not filter model outcomes.
VERBS=set('''typed rode grilled drew stirred explored drank swallowed attacked dusted counted raced
played painted parked cleaned smoked filmed wrestled fought chewed ate baked cheered mopped cooked
observed started taught practiced left pulled bathed groomed dried woke hid dressed washed settled
undressed shaved scratched calmed changed grew rolled turned shrank swung trained moved flooded
broke lit crashed hunted sailed performed ordered wrote steered studied juggled vacuumed embraced
cuddled met disrobed hugged kissed healed selected appointed manufactured merged captured inspired
financed displayed sent handed brought fed offered awarded assigned paid forgot remembered discovered
understood believed recalled noticed saw explained knew realized accepted found mentioned revealed
learned disclosed proved announced conceded declared showed recognized regretted repeated'''.split())


def unique_span(source,cue,span):
    a,b=span;words=normalized_words(source)[a:b];other=normalized_words(cue)
    starts=[i for i in range(len(other)-len(words)+1) if other[i:i+len(words)]==words]
    return [starts[0],starts[0]+len(words)] if len(starts)==1 else None


def build(root):
    parent=root.parent/'E54/data-v1.jsonl';qualified=root.parent/'E82/data-v1.jsonl'
    old={r['item_id']:r for r in map(json.loads,parent.read_text().splitlines())}
    newer=list(map(json.loads,qualified.read_text().splitlines()))
    groups=collections.defaultdict(list)
    for r in newer:
        if r['construction'] in ['NPZ','MVRR','NPS']:groups[r['source_unit']].append(r)
    locations={};excluded=[];ledger=[]
    gp_groups={uid:rr for uid,rr in groups.items() if rr[0]['condition']=='gp'}
    for uid,rr in sorted(gp_groups.items()):
        r=rr[0];words=normalized_words(r['sentence'])
        candidates=[i for i,w in enumerate(words) if w in VERBS]
        assert candidates,(uid,r['sentence'])
        vi=candidates[0]
        assert vi>0
        # Use only the already annotated physical disambiguator, never a model answer.
        disambs={x['step5_annotation']['disamb_word_index'] for x in rr
                 if x['step5_annotation'].get('disamb_word_index') is not None}
        if r['construction']=='MVRR':np=[0,vi]
        elif len(disambs)==1:
            di=next(iter(disambs));assert di>vi and di<len(words),(uid,vi,di)
            start=vi+1
            while start<di and words[start] in ['up','off','down']:start+=1
            end=next((i for i in range(start,di) if words[i] in ['who','that','which']),di)
            np=[start,end]
        else:
            excluded.append(dict(source_unit=uid,reason='Missing/conflicting existing physical disambiguator',disamb_indices=sorted(disambs)))
            continue
        assert np[0]<np[1] and not np[0]<=vi<np[1],(uid,np,vi)
        loc=dict(verb_span=[vi,vi+1],noun_span=np,verb_surface=words[vi],noun_surface=words[np[0]:np[1]],
                 GP_source_unit=uid,disamb_indices=sorted(disambs))
        locations[uid]=loc
        mates={x['source_unit'] for x in newer if x['condition']=='control' and
               x['analysis_pair_id']==r['analysis_pair_id'] and x['sentence_sha256']!=r['sentence_sha256']}
        assert len(mates)==1,(uid,mates)
        mate=next(iter(mates));cr=groups[mate][0]
        # Independent unique same-word spans also support the author's clause-reordered cue.
        vp=unique_span(r['sentence'],cr['sentence'],loc['verb_span'])
        nn=unique_span(r['sentence'],cr['sentence'],loc['noun_span'])
        if vp is None or nn is None or vp[0]<=nn[0]<vp[1] or nn[0]<=vp[0]<nn[1]:
            del locations[uid];excluded.append(dict(source_unit=uid,reason='Cue same-word span alignment unavailable'));continue
        assert len(vp)==2 and vp[1]-vp[0]==1
        cw=normalized_words(cr['sentence']);assert cw[vp[0]]==loc['verb_surface']
        assert cw[nn[0]:nn[1]]==loc['noun_surface']
        locations[mate]=dict(loc,verb_span=vp,noun_span=nn)
        ledger.append(dict(GP_source=uid,GP_sentence=r['sentence'],CUE_source=mate,CUE_sentence=cr['sentence'],
            construction=r['construction'],GP_verb_index=vi,GP_verb=words[vi],GP_noun_indices=np,
            GP_noun=words[np[0]:np[1]],CUE_verb_index=vp[0],CUE_noun_indices=nn,
            original_published_verb_field=r.get('source_gp_verb')))
    rows=[]
    for r in newer:
        if r['source_unit'] not in locations:continue
        mother=old[r['item_id']]
        for field in ['sentence','question','grounded_gold','analysis_cluster_id','analysis_question_target','analysis_pair_id']:
            assert r[field]==mother[field],(r['item_id'],field)
        rows.append(dict(mother,source_unit=r['source_unit'],frame_locator=locations[r['source_unit']],
            original_source_sent_type=r.get('source_sent_type'),original_source_question_type=r.get('source_question_type')))
    root.mkdir(exist_ok=True);out=root/'data-v1.jsonl';assert not out.exists()
    out.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (root/'location-ledger-v1.json').write_text(json.dumps(dict(locations=ledger,excluded=excluded),indent=2)+'\n')
    manifest=dict(data_sha256=sha(out),parent_E54_sha256=sha(parent),qualified_E82_sha256=sha(qualified),
        QA=len(rows),GP_sources=len(ledger),coverage=dict(collections.Counter(x['construction'] for x in ledger)),
        new_conditions=len(rows)*4*2*3,new_api_calls=0,code_sha256=sha(Path(__file__)),
        locators='Input-only finite surface inventory; existing disambiguator; exact-word GP/cue alignment; no new gold')
    (root/'data-v1.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest),flush=True)


def prepare(rows,tok):
    from prequestion_oracle_map import make_tasks
    from revision_interventions import word_character_spans,token_region
    parent_tasks,_=make_tasks(rows,tok)
    baseline=[t for t in parent_tasks if t['operation']=='CAUSAL'];selected=[]
    for t in baseline:
        r=t['row'];start=t['prompt'].index(r['sentence']);words=word_character_spans(r['sentence'])
        enc=tok(t['prompt'],return_offsets_mapping=True,add_special_tokens=not bool(tok.chat_template))
        for op,field in [('VERB_ONLY','verb_span'),('NOUN_ONLY','noun_span')]:
            a,b=r['frame_locator'][field];qs=token_region(enc['offset_mapping'],start+words[a][0],start+words[b-1][1])
            assert qs and set(qs)<=set(t['source_tokens'])
            selected.append(dict(t,operation=op,query_tokens=qs))
    assert len(selected)==len(rows)*8
    return selected,baseline


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();build(a.root)
