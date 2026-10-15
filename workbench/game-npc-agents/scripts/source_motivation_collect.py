#!/usr/bin/env python3
"""Preserve valid extractive DATA, including complete objects from truncated batches."""
import argparse
import json
from pathlib import Path

LEVELS = ['short_motivation','mid_motivation','long_motivation']
SCOPES = ['self','other','self_and_other','unspecified']


def decode_cases(content):
    try:
        value = json.loads(content)
        value = value.get('cases',value) if isinstance(value,dict) else value
        if isinstance(value,dict): value = [{'annotation_id':k,**v} for k,v in value.items()]
        return value
    except json.JSONDecodeError:
        # Only fully decoded objects are retained. Never finish or invent a cut-off object.
        key = content.find('"cases"')
        if key < 0: return []
        start = content.find(':',key)+1
        while start < len(content) and content[start].isspace(): start += 1
        if start >= len(content): return []
        kind = content[start]; position = start+1;decoder = json.JSONDecoder();rows = []
        while position < len(content):
            while position < len(content) and (content[position].isspace() or content[position]==','): position += 1
            if position >= len(content) or content[position] in ']}': break
            try:
                if kind == '[':
                    row,end = decoder.raw_decode(content,position)
                elif kind == '{':
                    aid,end = decoder.raw_decode(content,position)
                    while content[end].isspace(): end += 1
                    assert content[end] == ':'
                    end += 1
                    while content[end].isspace(): end += 1
                    value,end = decoder.raw_decode(content,end)
                    row = {'annotation_id':aid,**value}
                else: break
                rows.append(row);position = end
            except (ValueError,IndexError,AssertionError,TypeError): break
        return rows


def validate(row, source):
    row = json.loads(json.dumps(row))
    changes = []
    if set(row['motivation_levels']) == {'short','mid','long'}:
        row['motivation_levels']={k+'_motivation':v for k,v in row['motivation_levels'].items()}
        changes.append('explicit-level-key-aliases')
    assert set(row['motivation_levels']) == set(LEVELS)
    for level, label in row['motivation_levels'].items():
        if label.get('scope') in [level,level.removesuffix('_motivation')] and label.get('beneficiary') in SCOPES:
            # Explicit model output layout alias; no semantic label inferred or changed.
            label['original_scope_field'] = label['scope']
            label['scope'] = label['beneficiary'];changes.append(level+'/beneficiary-to-scope')
        assert label['scope'] in SCOPES, level+'/scope-enum'
        assert label['exact_quote'] in source[level], level+'/literal-quote'
        assert label['scope']=='unspecified' or bool(label['exact_quote']), level+'/missing-quote'
    assert row['support_claim'] in ['yes','no','unclear'], 'support-enum'
    assert row['request_quote'] in source['request_text'], 'request-literal-quote'
    assert any(row['motivation_quote'] in source[level] for level in LEVELS), 'motivation-literal-quote'
    assert row['support_claim']!='yes' or (row['request_quote'] and row['motivation_quote']), 'support-missing-quotes'
    return row,changes


def main():
    ap = argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True)
    ap.add_argument('--additional-run',type=Path,action='append',default=[])
    args = ap.parse_args()
    public = {r['annotation_id']:r for r in json.loads((args.run/'public_data.json').read_text())}
    labels, rejected, changes, requests, sources = {}, [], [], [], {}
    folders = [folder for run in [args.run,*args.additional_run] for folder in sorted(run.glob('batch_*'))]
    for folder in folders:
        if not (folder/'metadata.json').exists(): continue
        metadata = json.loads((folder/'metadata.json').read_text());requests.append(metadata)
        if metadata.get('http_status')!=200: continue
        response = json.loads((folder/'response.json').read_text())
        content = response['choices'][0]['message']['content']
        requested = {r['annotation_id'] for r in json.loads(json.loads((folder/'request.json').read_text())['messages'][1]['content'])}
        for raw in decode_cases(content):
            aid = raw.get('annotation_id')
            try:
                assert aid in requested and aid not in labels
                row,normalization = validate(raw,public[aid]);labels[aid] = row
                sources[aid] = str(folder)
                if normalization: changes.append({'annotation_id':aid,'normalization':normalization,'source_batch':str(folder)})
            except (AssertionError,KeyError,TypeError) as exc:
                rejected.append({'annotation_id':aid,'source_batch':str(folder),'error_type':type(exc).__name__, 'reason':str(exc), 'raw':raw})
    missing = sorted(set(public)-set(labels))
    (args.run/'derived_valid_labels.json').write_text(json.dumps(list(labels.values()),ensure_ascii=False,indent=2)+'\n')
    summary = {'expected_rows':len(public),'valid_rows':len(labels),'missing_ids':missing,
        'rejected_raw_rows':rejected,'layout_normalizations':changes,
        'label_sources': sources,
        'requests_completed':len(requests),'total_tokens':sum((r.get('usage') or {}).get('total_tokens',0) for r in requests),
        'cash_endpoint_calls':0,'npc_cloud_calls':0,
        'scope':'Extractive source-text DATA; original labels/raw failures kept; no utility or action correctness judgment.'}
    (args.run/'collection.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'valid':len(labels),'missing':len(missing),'rejected':len(rejected),
                      'normalized_rows':len(changes),'tokens':summary['total_tokens']}))


if __name__ == '__main__': main()
