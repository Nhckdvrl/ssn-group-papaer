#!/usr/bin/env python3
"""Preserve blind labels and normalize JSON containers; no new model calls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def collect(root):
    public = {r['annotation_id']:r for r in json.loads((root/'public_data.json').read_text())}
    rows, batches = {}, []
    for d in sorted(root.glob('labels_*')):
        response = d/'response.json'
        if not response.exists(): continue
        result = json.loads(response.read_text())
        if 'choices' not in result: continue
        expected = {r['annotation_id'] for r in json.loads(json.loads((d/'request.json').read_text())['messages'][1]['content'])}
        try:
            x = json.loads(result['choices'][0]['message']['content'])
        except (KeyError, json.JSONDecodeError): continue
        x = x.get('cases',x) if isinstance(x,dict) else x
        notes = []
        if isinstance(x,dict):
            labels = []
            for aid, r in x.items():
                if not isinstance(r,dict): continue
                r = dict(r)
                if 'annotation_id' not in r: r['annotation_id'] = aid
                labels.append(r)
            notes.append('ID-keyed JSON object normalized to rows; labels unchanged')
        elif isinstance(x,list): labels = x
        else: continue
        present = {r.get('annotation_id') for r in labels}
        missing, unknown = expected-present, present-expected
        # A single mistyped ID can be matched only by a nonempty literal source quote.
        # No positional matching or assignment from outcomes/model/persona is permitted.
        if len(missing)==len(unknown)==1:
            target = next(iter(missing)); bad = next(iter(unknown))
            candidate = next(r for r in labels if r.get('annotation_id')==bad)
            quotes = [(s,candidate.get(s,{}).get('evidence','')) for s in ['speech','memory']]
            exact = [(s,q) for s,q in quotes if len(q)>=8 and q in public[target][s]]
            if exact and all(sum(q in public[e][s] for e in expected)==1 for s,q in exact):
                candidate['annotation_id'] = target
                notes.append({'ID_typo':bad,'source_ID':target,'basis':'unique nonempty literal quote within original batch'})
        valid = []
        for r in labels:
            aid = r.get('annotation_id')
            if aid not in expected: continue
            try:
                assert r['stance'] in ['accept_now','decline','conditional','unclear']
                flags = {}
                for stage in ['speech','memory']:
                    for goal in ['own_state','request_state']:
                        assert r[stage][goal] in ['pending','completed','no_claim','ambiguous']
                    quote = r[stage]['evidence']; assert isinstance(quote,str)
                    flags[stage] = bool(quote in public[aid][stage] or all(q in public[aid][stage] for q in quote.split(' / ')))
                quote = r['reinterpretation_quote']; assert isinstance(quote,str)
                flags['reinterpretation'] = not quote or any(quote in public[aid][s] for s in ['speech','memory'])
            except (AssertionError,KeyError,TypeError): continue
            assert aid not in rows, 'duplicate annotation ID'
            r['quote_validation'] = flags; r['batch'] = d.name
            rows[aid] = r; valid.append(r)
        batches.append({'batch':d.name,'expected':len(expected),'linked_labels':len(valid),'format_notes':notes,
                        'response_sha256':hashlib.sha256(response.read_bytes()).hexdigest()})
        (d/'parsed_recovered.json').write_text(json.dumps(valid,ensure_ascii=False,indent=2)+'\n')
    return public, rows, batches


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--require-complete',action='store_true'); a=ap.parse_args()
    public, rows, batches = collect(a.directory)
    native_map = json.loads((a.directory/'private_mapping.json').read_text())
    anchors = json.loads((a.directory/'anchor_expected.json').read_text())
    report = {'native_rows':sum(k in rows for k in native_map),'expected_native_rows':720,
              'anchors':{},'batches':batches,'quote_review_rows':sum(not all(r['quote_validation'].values()) for r in rows.values()),
              'source_directory':str(a.directory),'complete':set(rows)==set(public),'npc_cloud_calls':0,'cash_endpoint_calls':0,
              'scope':'semantic labels describe generated text, never define physical execution or normative persona behavior'}
    for aid, expected in anchors.items():
        if aid in rows:
            actual={'stance':rows[aid]['stance'],'memory_request_state':rows[aid]['memory']['request_state']}
            report['anchors'][aid]={'expected':expected,'actual':actual,'exact_match':actual==expected}
    native = [rows[k] for k in native_map if k in rows]
    report['counts'] = {'stances':dict(Counter(r['stance'] for r in native)),
                       'memory_request_state':dict(Counter(r['memory']['request_state'] for r in native)),
                       'memory_own_state':dict(Counter(r['memory']['own_state'] for r in native)),
                       'speech_request_state':dict(Counter(r['speech']['request_state'] for r in native))}
    (a.directory/'labels_collected.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['batches','anchors']},ensure_ascii=False))
    if a.require_complete: assert report['complete'], 'Missing/invalid labels preserved; no fabricated rows'


if __name__=='__main__': main()
