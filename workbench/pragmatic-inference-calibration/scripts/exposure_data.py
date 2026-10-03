"""E57 language-only parent exposure; all semantic modifications are explicit."""
import hashlib
import json
import random
from pathlib import Path
from noisy_parent_data import ROOT, specs, tokenizer_path, sha

SEEDS=(20261003,20261004)


def prepare(root,tok):
    src=root/'data/E56-original-exposure-materials.json'
    groups=json.loads(src.read_text());assert len(groups)==8
    audit=json.loads((Path(__file__).resolve().parents[1]/'results/E56-original-exposure-audit.json').read_text())
    assert audit['export_sha256']==sha(src)
    families=sorted({x['family'] for x in groups})
    reference={x['family']:x for x in groups if x['context']=='clean'}
    control=reference[families[0]]['controls']
    assert all(reference[f]['controls']==control for f in families)
    rows=[]
    for context in ('clean','noisy'):
        selected={x['family']:x for x in groups if x['context']==context}
        fillers=selected[families[0]]['fillers']
        assert all(selected[f]['fillers']==fillers for f in families)
        for seed in SEEDS:
            order=list(range(48));random.Random(seed).shuffle(order)
            history='Earlier sentences in this task:\n'+'\n'.join(fillers[j]['Input.trial_'] for j in order)
            for goal in ('default','literal'):
                task='Please simply answer "Yes" or "No" to the question.\n'
                if goal=='literal':task+='Answer the question using the sentence exactly as written, even if it describes an unlikely event.\n'
                materials=[('critical',family,r) for family in families for r in selected[family]['critical']]
                materials += [('control','shared-active-passive',r) for r in control]
                for kind,family,r in materials:
                    sentence=r['Input.trial_'];question=r['Input.question_1_']
                    # Final utterance/question bytes are identical across context and seed.
                    prompt=task+history+'\n\nSentence: '+sentence+'\nQuestion: '+question
                    rendered=tok.apply_chat_template([{'role':'user','content':prompt}],
                        tokenize=False,add_generation_prompt=True,enable_thinking=False)
                    ids=tok.encode(rendered,add_special_tokens=False)
                    assert ids and len(ids)+8<4096 and r['CorrectAnswer1'] in ('Yes','No')
                    rows.append({'id':'/'.join((family,r['Item'],r['Condition'],context,str(seed),goal)),
                        'kind':kind,'family':family,'source':r,'context':context,'seed':seed,'goal':goal,
                        'literal_answer':r['CorrectAnswer1'],'input_ids':ids,
                        'prompt_sha256':hashlib.sha256(rendered.encode()).hexdigest(),
                        'history_sha256':hashlib.sha256(history.encode()).hexdigest()})
    assert len(rows)==len({r['id'] for r in rows})==2944
    for family in families:
        assert selected[family]['critical']==reference[family]['critical']
    return rows,{'source_file':str(src),'source_sha256':sha(src),'n_critical':320,
        'n_unique_critical_item_clusters':80,'n_control_variants':48,'n_control_items':12,
        'n_filler_slots':48,'n_changed_filler_slots':18,'seeds':SEEDS,'n':2944}


def fingerprint(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()


if __name__=='__main__':
    from transformers import AutoTokenizer,AutoConfig
    out=Path(__file__).resolve().parents[1]/'results/E57-source-preflight.json';assert not out.exists()
    audits={}
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1];p=ROOT/'models'/cp
        marker=json.loads((p/'DOWNLOAD_COMPLETE.json').read_text())
        assert marker['model']==m['id'] and marker['revision']==m['sha']
        native=AutoTokenizer.from_pretrained(p,local_files_only=True)
        common=AutoTokenizer.from_pretrained(tokenizer_path(ROOT,cp),local_files_only=True)
        assert native.backend_tokenizer.to_str()==common.backend_tokenizer.to_str()
        rows,source=prepare(ROOT,common)
        maximum=max(len(r['input_ids']) for r in rows)
        assert maximum+8<AutoConfig.from_pretrained(p,local_files_only=True).max_position_embeddings
        audits[cp]={'input_sha256':fingerprint(rows),'source_audit':source,'max_tokens':maximum,
            'backend_sha256':hashlib.sha256(common.backend_tokenizer.to_str().encode()).hexdigest()}
    out.write_text(json.dumps({'models':specs(ROOT),'audits':audits,'helper_sha256':sha(Path(__file__)),
        'gate_pass':True},indent=2)+'\n')
    print(json.dumps({k:v['max_tokens'] for k,v in audits.items()}))
