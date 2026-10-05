"""Jurayj canonical component generator + conservative interpretation readouts.

The syntax-role NPS readout deliberately avoids treating understand NP and
understand that S as mutually exclusive semantic propositions.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import numpy as np
from data import CACHE, record, read_table, verified_root, write_jsonl, sha
from analyze import estimate

# Pre-inference linguistic audit; no exclusions based on model performance.
FLAGS={
    'NPZ:26':'In case conditional: dropping conditional antecedent does not preserve assertion truth',
    'NPZ:36':'In case conditional: dropping conditional antecedent does not preserve assertion truth',
    'NPZ:41':'In case conditional: dropping conditional antecedent does not preserve assertion truth',
    'NPS:17':'insured used with clausal complement; possible insure/ensure lexical issue',
    'MVRR:9':'sketched/drawn a portrait has doubtful recipient passive with artist',
    'MVRR:12':'composed a carefully worded excuse has doubtful recipient passive with student',
    'MVRR:14':'performed an unsolicited favor has doubtful recipient passive with boys',
    'MVRR:17':'jumped/leapt completely past has doubtful transitive/passive licensing',
    'MVRR:18':'prepared/gotten a dinner has doubtful recipient passive with students',
    'MVRR:26':'stitched/woven a shawl has doubtful recipient passive with girl',
}
NON_OBJECT_BLOCKERS={4:'PP',12:'PP',24:'PP',25:'adverb',28:'infinitive',30:'adverb',32:'infinitive',33:'adverb',35:'PP',40:'PP'}
ACTIVE_PAST={'given':'gave','taken':'took','beaten':'beat','grown':'grew','eaten':'ate','sworn':'swore',
             'forgotten':'forgot','ridden':'rode','drawn':'drew','driven':'drove','known':'knew',
             'written':'wrote','begun':'began','done':'did','thrown':'threw','bitten':'bit',
             'leapt':'leapt','gotten':'got','woken':'woke','hidden':'hid','seen':'saw','blown':'blew',
             'shrunk':'shrank','sunk':'sank','shown':'showed','woven':'wove','flown':'flew','borne':'bore'}

def join(parts):return ' '.join(' '.join(parts).split())
def terminal(text):return text.rstrip('.').strip()+'.'

def canonical(row,family,condition,extension):
    """Same upstream component selection; collapse only trailing repeated periods."""
    if family=='NPZ':
        verb=row['Intransitive Verb'] if condition=='non_gp' else row['Transitive Verb']
        pre=join([row['Start'],verb]+([row['Blocker']] if condition=='blocked' else []))
        if condition=='explicit_cue':pre+=row['Comma']
        before=join([pre,row['NP/Z']]+([row['Extension']] if extension else []))
        after=join([row['Verb'],row['Rest']]);amb_start=len(pre.split())
    elif family=='NPS':
        verb=row['Unambiguous Verb'] if condition=='blocked' else row['Ambiguous Verb']
        pre=join([row['Subject'],verb]+([row['That']] if condition=='explicit_cue' else []))
        before=join([pre,row['NP/S']]+([row['Extension']] if extension else []))
        after=join([row['Disambiguator'],row['Rest']]);amb_start=len(pre.split())
    else:
        verb=row['Unambiguous verb'] if condition=='blocked' else row['Ambiguous verb']
        pre=join([row['Start'],row['Noun']]+([row['Unreduced content']] if condition=='explicit_cue' else []))
        before=join([pre,verb,row['RC contents']]+([row['Intervener']] if extension else []))
        after=join([row['Disambiguator'],row['End']]);amb_start=len(pre.split())
    sentence=terminal(before+' '+after)
    return sentence,amb_start,len(before.split())

def claims(row,family,condition):
    if family=='NPZ':
        subject=re.sub(r'^(?:As long as|Even though|In case|As|When|After|Though|While|Because|Although|As long as|Once|Before)\s+','',row['Start'])
        initial=terminal(join([subject,row['Transitive Verb'],row['NP/Z']]))
        final=terminal(join([row['NP/Z'],row['Verb'],row['Rest']]))
        return initial,final,{
            'lingering':f'In this sentence, is "{row["NP/Z"]}" the direct object of "{row["Transitive Verb"]}"?',
            'intended':f'In this sentence, is "{row["NP/Z"]}" the subject of the main clause?',
            'lingering_semantic':f'Does this sentence state that {initial[0].lower()+initial[1:-1]}?',
            'intended_semantic':f'Does this sentence state that {final[0].lower()+final[1:-1]}?'}
    if family=='NPS':
        verb=row['Unambiguous Verb'] if condition=='blocked' else row['Ambiguous Verb']
        initial=f'"{row["NP/S"]}" is the direct object of "{verb}".'
        final=f'"{row["NP/S"]}" is the subject of the embedded clause.'
        # Keep a grammatical object-taking verb in this semantic diagnostic.
        # In the lexical condition its absence is a confound, reported explicitly.
        initial_sem=terminal(join([row['Subject'],row['Ambiguous Verb'],row['NP/S']]))
        final_sem=terminal(join([row['Subject'],verb,'that',row['NP/S'],row['Disambiguator'],row['Rest']]))
        return initial,final,{
            'lingering':f'In this sentence, is "{row["NP/S"]}" the direct object of "{verb}"?',
            'intended':f'In this sentence, is "{row["NP/S"]}" the subject of the clause "{join([row["Disambiguator"],row["Rest"]])}"?',
            'lingering_semantic':f'Does this sentence state that {initial_sem[0].lower()+initial_sem[1:-1]}?',
            'intended_semantic':f'Does this sentence state that {final_sem[0].lower()+final_sem[1:-1]}?'}
    verb=row['Unambiguous verb'] if condition=='blocked' else row['Ambiguous verb']
    subject=join([row['Start'],row['Noun']])
    aux=row['Unreduced content'].split()[-1]
    initial=terminal(join([subject,ACTIVE_PAST.get(verb,verb),row['RC contents']]))
    final=terminal(join([subject,aux,verb,row['RC contents']]))
    simple=terminal(join([subject,row['Disambiguator'],row['End']]))
    return initial,final,{
        'lingering':f'In this sentence, is "{verb}" a finite active verb with "{subject}" as its subject?',
        'intended':f'In this sentence, is "{verb}" part of a passive relative clause modifying "{subject}"?',
        'lingering_semantic':f'Does this sentence state that {initial[0].lower()+initial[1:-1]}?',
        'intended_semantic':f'Does this sentence state that {final[0].lower()+final[1:-1]}?',
        'simple':f'Does this sentence state that {simple[0].lower()+simple[1:-1]}?'}

def build(cache):
    root=verified_root(cache,'jurayj');out=[];components=[]
    for family,file in [('NPZ','npz.tsv'),('NPS','nps.tsv'),('MVRR','vawip.tsv')]:
        for i,raw in enumerate(read_table(root/file),1):
            row={k:v.strip() for k,v in raw.items()};sid=f'{family}:{i}'
            components.append({'pair_id':sid,'source':'jurayj','file':file,'source_row_id':i,'components':row,'flag':FLAGS.get(sid)})
            conditions=['gp','explicit_cue','blocked']+(['non_gp'] if family=='NPZ' else [])
            for condition in conditions:
                for extended in (False,True):
                    sentence,start,disamb=canonical(row,family,condition,extended)
                    initial,final,questions=claims(row,family,condition)
                    ext=row['Intervener'] if family=='MVRR' else row['Extension']
                    cue={'NPZ':'comma','NPS':'that','MVRR':'unreduced'}[family] if condition=='explicit_cue' else ('lexical_selection' if condition=='blocked' and family!='NPZ' or condition=='non_gp' else 'object_slot' if condition=='blocked' else 'none')
                    for qtype,q in questions.items():
                        diagnostic=qtype=='lingering_semantic' and family in ('NPS','MVRR')
                        gold=None if diagnostic or sid in FLAGS else 'No' if qtype.startswith('lingering') else 'Yes'
                        if family=='NPS':structural_initial,structural_final=initial,final
                        elif family=='NPZ':
                            structural_initial=f'"{row["NP/Z"]}" is the direct object of "{row["Transitive Verb"]}".'
                            structural_final=f'"{row["NP/Z"]}" is the subject of the main clause.'
                        else:
                            active_verb=row['Unambiguous verb'] if condition=='blocked' else row['Ambiguous verb']
                            structural_initial=f'"{active_verb}" is a finite active verb with "{join([row["Start"],row["Noun"]])}" as subject.'
                            structural_final=f'"{active_verb}" is in a passive relative clause.'
                        out.append(record(item_id=f'jurayj:{sid}:{condition}:{int(extended)}:{qtype}',source='jurayj',
                            construction=family,condition=condition,sentence=sentence,question_type=qtype,question=q,
                            gold=gold,initial_parse_claim=structural_initial,final_parse_claim=structural_final,
                            ambiguity_start=start,disambiguator_index=disamb,cue_type=cue,
                            extension_length=len(ext.split()) if extended else 0,extended=extended,
                            source_row_id=f'{file}:{i}',pair_id=sid,audit_flag=FLAGS.get(sid),
                            clean_stratum=sid not in FLAGS,
                            blocker_class=NON_OBJECT_BLOCKERS.get(i,'direct_object') if family=='NPZ' and condition=='blocked' else None,
                            readout_kind='syntactic_role' if qtype in ('intended','lingering') else 'asserted_proposition',
                            diagnostic_only=diagnostic,gold_status='unverified' if sid in FLAGS else 'diagnostic_no_gold' if diagnostic else 'audited',
                            lexical_absence_control=(family=='NPZ' and condition=='non_gp') or (family=='NPS' and condition=='blocked' and qtype=='lingering_semantic')))
    return out,components

def validate(rows,components,cache):
    assert len(components)==90
    assert len({r['item_id'] for r in rows})==len(rows)
    counts=collections.Counter(r['construction'] for r in rows)
    assert counts=={'NPZ':43*8*4,'NPS':19*6*4,'MVRR':28*6*5},counts
    # No post-result filtering; flags fixed in this source before any E01 run.
    for r in rows:
        assert r['disambiguator_index']>r['ambiguity_start']
        assert 'nan' not in r['sentence'].split()
        if r['gold_status']=='audited':assert r['gold']==('No' if r['question_type'].startswith('lingering') else 'Yes')
    # Compare all canonical variants with actual upstream make_sents.py.
    import importlib.util,contextlib,io
    root=verified_root(cache,'jurayj')
    spec=importlib.util.spec_from_file_location('upstream_make_sents',root/'make_sents.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    byid={r['item_id']:r for r in rows}
    for family,file,fn in [('NPZ','npz',mod.make_sents_npz),('NPS','nps',mod.make_sents_nps),('MVRR','vawip',mod.make_sents_va)]:
        for condition in ['gp','explicit_cue','blocked']+(['non_gp'] if family=='NPZ' else []):
            for ext in (False,True):
                if family=='NPZ':kw=dict(sent_type={'gp':'gp','explicit_cue':'gp','blocked':'blocked','non_gp':'intransitive'}[condition],comma=condition=='explicit_cue',extension=ext)
                elif family=='NPS':kw=dict(sent_type='unambiguous' if condition=='blocked' else 'gp',that=condition=='explicit_cue',extension=ext)
                else:kw=dict(sent_type='unambiguous' if condition=='blocked' else 'gp',unreduced=condition=='explicit_cue',intervener=ext)
                with contextlib.redirect_stdout(io.StringIO()):sents=fn(filename=str(root/file),**kw)
                for i,s in enumerate(sents,1):
                    actual=byid[f'jurayj:{family}:{i}:{condition}:{int(ext)}:intended']['sentence']
                    assert actual==terminal(join([s])),(family,i,condition,ext,actual,s)
    return dict(component_rows=90,qa_rows=len(rows),counts=dict(counts),unique_sentence_variants=len({(r['pair_id'],r['condition'],r['extended']) for r in rows}),
                canonical_parity='all variants match pinned make_sents.py after whitespace / repeated-final-period normalization',
                flags=FLAGS,hash_audit='verified before loading')

def tasks_jurayj(path,tokenizer,experiment):
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    # Unverified/ill-formed sentences remain in the generation ledger, never scored.
    rows=[r for r in rows if r['clean_stratum']]
    root=verified_root(CACHE,'amouyal');tasks=[]
    for order,file in [('reg','prefixes.json'),('rev','prefixes_rev.json')]:
        pref=json.loads((root/'prefixes'/file).read_text())[0]
        for r in rows:
            q=pref['question'].replace('SENTENCE',r['sentence']).replace('QUESTION',r['question'])
            tasks.append((r,f'raw_{order}_0',pref['system']+'\n\n'+q+'\n\n'+pref['suffix']))
            for repair in (False,True):
                from infer import REPAIR
                system=pref['system']+('\n\n'+REPAIR if repair else '')
                chat=tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':q}],
                    tokenize=False,add_generation_prompt=True,enable_thinking=False)+pref['suffix']
                tasks.append((r,f'chat_{order}'+('_repair' if repair else ''),chat))
    return tasks

def analyze_jurayj(rows):
    out={'cells':{},'paired_effects':{},'joint':{}}
    for stratum in ('all','clean'):
        for suite in ('raw','chat','chat_repair'):
            selected=[r for r in rows if (stratum=='all' or r['clean_stratum']) and (r['prompt_id'].startswith('raw_') if suite=='raw' else r['prompt_id'].startswith('chat_') and r['prompt_id'].endswith('repair')==(suite=='chat_repair'))]
            sets=collections.defaultdict(lambda:collections.defaultdict(list))
            for r in selected:sets[r['pair_id']][(r['construction'],r['condition'],r['extended'],r['question_type'])].append(r)
            averaged={sid:{k:np.mean([r['p_yes'] for r in rr]) for k,rr in cells.items()} for sid,cells in sets.items()}
            for key in sorted({k for d in averaged.values() for k in d}):
                family,c,e,q=key
                out['cells'][f'{stratum}/{suite}/{family}/{c}/{int(e)}/{q}']=estimate([d[key] for d in averaged.values() if key in d])
            for family in ('NPZ','NPS','MVRR'):
                ds=[d for d in averaged.values() if any(k[0]==family for k in d)]
                for q in ('intended','lingering','intended_semantic','lingering_semantic'):
                    for c in ('explicit_cue','blocked'):
                        for e in (False,True):
                            out['paired_effects'][f'{stratum}/{suite}/{family}/{c}_minus_gp/{int(e)}/{q}']=estimate([d[(family,c,e,q)]-d[(family,'gp',e,q)] for d in ds])
                    for c in ('gp','explicit_cue','blocked'):
                        out['paired_effects'][f'{stratum}/{suite}/{family}/{c}/extension_minus_short/{q}']=estimate([d[(family,c,True,q)]-d[(family,c,False,q)] for d in ds])
                    out['paired_effects'][f'{stratum}/{suite}/{family}/extension_DiD_gp_minus_cue/{q}']=estimate([d[(family,'gp',True,q)]-d[(family,'gp',False,q)]-d[(family,'explicit_cue',True,q)]+d[(family,'explicit_cue',False,q)] for d in ds])
                for c in ('gp','explicit_cue','blocked'):
                    for e in (False,True):
                        # Joint correctness at each fixed prompt, then average within item.
                        vals=[]
                        for sid,d in sets.items():
                            ik=(family,c,e,'intended');lk=(family,c,e,'lingering')
                            if ik not in d:continue
                            ii={r['prompt_id']:r for r in d[ik]};ll={r['prompt_id']:r for r in d[lk]}
                            vals.append(np.mean([int(ii[p]['p_yes']>.5 and ll[p]['p_yes']>.5) for p in ii]))
                        out['joint'][f'{stratum}/{suite}/{family}/{c}/{int(e)}/final_correct_and_initial_supported']=estimate(vals)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=CACHE);args=ap.parse_args()
    rows,components=build(args.cache);report=validate(rows,components,args.cache)
    write_jsonl(args.cache/'normalized/jurayj.jsonl',rows)
    write_jsonl(args.cache/'normalized/jurayj-components.jsonl',components)
    report['normalized_sha256']=sha(args.cache/'normalized/jurayj.jsonl')
    (args.cache/'jurayj-generation-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
