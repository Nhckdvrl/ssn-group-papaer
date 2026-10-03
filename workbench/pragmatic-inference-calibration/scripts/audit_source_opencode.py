"""E58 finite, blinded, per-item auxiliary audit via the official free-model CLI."""
import hashlib
import json
import os
import random
import subprocess
from pathlib import Path

ROOT = Path('/data1/xiangding/work/pragmatic-inference-calibration')
MODEL = 'opencode/ling-3.1-flash-free'
SEED = 20261003
KEYS = {'id', 'event_role_answer', 'world_entailment', 'literal_paraphrase',
        'question_role', 'repair_possible', 'repair_description', 'ambiguity', 'evidence_quote'}
INSTRUCTIONS = '''Audit ONE original psycholinguistic sentence/question pair. Do not use tools.
Return one JSON object, without prose or markdown. Do not invent a context.
Separate two questions: (1) Does the question correctly describe participant roles in the
specific event explicitly described? (event_role_answer: Yes / No / ambiguous)
(2) Does the sentence logically entail the answer to the question about the world?
(world_entailment: yes / no / underdetermined). Failure to state a second reciprocal
event does not logically rule it out. For instance, a described agent acting on a patient
does not establish that the patient never performs that action in the world.
Give the sentence's literal role-based paraphrase; map the queried roles explicitly.
Separately say whether a plausible communicative repair could suggest another reading;
do not silently replace the literal sentence with that repair. repair_possible is boolean.
repair_description is a string (empty if none). ambiguity describes lexical/syntactic/
world-assumption issues, or is empty if none. evidence_quote is ONE nonempty EXACT
substring of the original sentence grounding your literal analysis, not a paraphrase.
Required keys: id, event_role_answer, world_entailment, literal_paraphrase, question_role,
repair_possible, repair_description, ambiguity, evidence_quote. The last six descriptive
fields other than repair_possible are strings. Use exactly the supplied opaque id.
This is candidate annotation, not human gold; admit uncertainty.
Input:
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare():
    path = ROOT/'data/E56-original-exposure-materials.json'
    groups = json.loads(path.read_text())
    clean = sorted((g for g in groups if g['context']=='clean'), key=lambda g:g['family'])
    rng = random.Random(SEED)
    selected = []
    for g in clean:
        item = rng.choice(sorted({r['Item'] for r in g['critical']}))
        rows = [r for r in g['critical'] if r['Item']==item]
        assert len(rows)==4
        for r in rows:
            selected.append({'kind':'critical','family':g['family'],'source':r})
    controls = clean[0]['controls']
    items = rng.sample(sorted({r['Item'] for r in controls}),4)
    for item in items:
        r = rng.choice([r for r in controls if r['Item']==item])
        selected.append({'kind':'control','family':'shared-active-passive','source':r})
    assert len(selected)==20
    plans = []
    for i,r in enumerate(selected):
        visible = {'id':f'A{i+1:04d}','sentence':r['source']['Input.trial_'],
                   'question':r['source']['Input.question_1_']}
        prompt = INSTRUCTIONS + json.dumps(visible,ensure_ascii=False)
        plans.append({**r,'visible':visible,'prompt':prompt,'prompt_sha256':sha(prompt.encode())})
    return plans, sha(path.read_bytes())


def main():
    out = ROOT/'data/E58-blind-source-audit'
    out.mkdir()  # Never overwrite/reuse partial results as successful replication.
    plans, source_sha = prepare()
    config = {'model':MODEL,'opencode_version':subprocess.check_output(['opencode','--version'],text=True).strip(),
              'source_sha256':source_sha,'seed':SEED,'n':20,'script_sha256':sha(Path(__file__).read_bytes()),
              'prompt_template_sha256':sha(INSTRUCTIONS.encode()),'not_gold':True,'complete':False}
    (out/'plans.json').write_text(json.dumps(plans,indent=2,ensure_ascii=False)+'\n')
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    env = dict(os.environ)
    env['OPENCODE_CONFIG_CONTENT'] = json.dumps({'permission':{'*':'deny'}})
    rows = []; failures = 0
    for p in plans:
        opaque = p['visible']['id']
        result = {'id':opaque,'prompt_sha256':p['prompt_sha256'],'usable_candidate':False}
        with (out/(opaque+'.events.jsonl')).open('w') as stdout, (out/(opaque+'.stderr')).open('w') as stderr:
            try:
                run = subprocess.run(['opencode','run','--pure','--format','json','--dir',str(out),
                                      '--model',MODEL,p['prompt']],env=env,stdout=stdout,stderr=stderr,timeout=75)
                result['returncode'] = run.returncode
            except subprocess.TimeoutExpired:
                result['error'] = 'timeout75'
        events = []
        for line in (out/(opaque+'.events.jsonl')).read_text().splitlines():
            try:events.append(json.loads(line))
            except ValueError:pass
        text = ''.join(e.get('part',{}).get('text','') for e in events if e.get('type')=='text')
        finishes = [e['part'] for e in events if e.get('type')=='step_finish']
        errors = [e.get('error',{}).get('data',{}).get('message') for e in events if e.get('type')=='error']
        result.update(text=text,step_costs=[e.get('cost') for e in finishes],provider_errors=errors)
        paid = any(e.get('cost') not in (0,None) for e in finishes)
        try:
            assert result.get('returncode')==0 and not errors and finishes
            assert all(e.get('cost')==0 for e in finishes),'cost not explicitly zero'
            assert not any(e.get('type')=='tool_use' or e.get('part',{}).get('type')=='tool' for e in events)
            a = json.loads(text)
            assert set(a)==KEYS and a['id']==opaque
            assert a['event_role_answer'] in ('Yes','No','ambiguous')
            assert a['world_entailment'] in ('yes','no','underdetermined')
            assert type(a['repair_possible']) is bool
            assert all(isinstance(a[k],str) for k in KEYS-{'repair_possible'})
            assert a['evidence_quote'] and a['evidence_quote'] in p['visible']['sentence']
            result.update(annotation=a,usable_candidate=True)
        except (AssertionError,ValueError,KeyError,TypeError) as e:
            result['gate_error'] = type(e).__name__
        failures = 0 if result['usable_candidate'] else failures+1
        rows.append(result)
        with (out/'annotations.jsonl').open('a') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
        print(json.dumps({'item':opaque,'usable_candidate':result['usable_candidate'],'costs':result['step_costs']}),flush=True)
        if paid or failures>=3:
            config['stop_reason'] = 'nonzero_cost' if paid else 'three_consecutive_failures'
            break
    config.update(attempted=len(rows),usable_candidates=sum(r['usable_candidate'] for r in rows),complete=len(rows)==20)
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')


if __name__=='__main__':
    main()
