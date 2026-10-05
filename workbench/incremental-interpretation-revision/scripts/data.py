"""Audited local-cache loaders. No upstream stimuli are vendored in this repo."""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import subprocess

CACHE = Path('/data1/xiangding/work/incremental-interpretation-revision')
SOURCES = {
    'amouyal': ('https://github.com/samsam3232/comparing_humans_llms_processing_difficulties', '072efefa01cb9716c2d14752eb1d4bf9830b0b81', 'MIT'),
    'jurayj': ('https://github.com/wjurayj/garden-path-gpt2', 'ad30c4248df5dcdda163bd6f05add419e1210c42', 'Apache-2.0'),
    'turing': ('https://github.com/microsoft/turing-experiments', 'f00115e793f5f728eccf13044bb299d64901de57', 'MIT'),
}

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def read_table(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t' if Path(path).suffix == '.tsv' else ','))

def audit(cache):
    out = {'date': '2026-10-05', 'sources': {}}
    for name, (url, revision, license_name) in SOURCES.items():
        root = cache / 'upstream' / name
        actual = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        assert actual == revision, (name, actual, revision)
        files = ['LICENSE', 'README.md']
        if name == 'amouyal':
            files += [str(p.relative_to(root)) for p in sorted((root/'data').glob('*.csv'))]
            files += [str(p.relative_to(root)) for p in sorted((root/'prefixes').glob('*.json'))]
            files += ['constants.py', 'inference/utils.py', 'inference/textgen_inference/fastchat_inference.py']
        elif name == 'jurayj':
            files += ['npz.tsv', 'nps.tsv', 'vawip.tsv', 'make_sents.py']
        else:
            files += ['data/external/garden_path/Christianson_2001.tsv', 'data/external/garden_path/Alternates_2022.tsv']
        report = {'url': url, 'revision': actual, 'license': license_name, 'files': {}}
        for rel in files:
            p = root/rel
            # sparse checkout may omit a root file: read the exact pinned blob.
            if not p.exists():
                p.write_bytes(subprocess.check_output(['git', '-C', str(root), 'show', f'{revision}:{rel}']))
            d = {'sha256': sha(p), 'bytes': p.stat().st_size}
            if p.suffix in ('.csv', '.tsv'):
                rows = read_table(p)
                d.update(rows=len(rows), columns=list(rows[0]),
                         empty_cells={k: sum(not str(r.get(k, '')).strip() for r in rows) for k in rows[0]},
                         duplicate_rows=len(rows)-len({json.dumps(r, sort_keys=True) for r in rows}))
                d['counts'] = {k: dict(collections.Counter(r[k] for r in rows)) for k in ['set_id', 'sent_type', 'quest_type', 'correct_answer', 'Label'] if k in rows[0]}
                if 'sentence' in rows[0] or 'Sentence' in rows[0]:
                    key = 'sentence' if 'sentence' in rows[0] else 'Sentence'
                    lengths = [len(r[key].split()) for r in rows]
                    d['unique_sentences'] = len({r[key] for r in rows})
                    d['word_length'] = {'min': min(lengths), 'max': max(lengths), 'mean': sum(lengths)/len(lengths)}
            report['files'][rel] = d
        out['sources'][name] = report
    return out

def verified_root(cache, source):
    manifest = json.loads((cache/'audit.json').read_text())
    assert manifest['sources'][source]['revision'] == SOURCES[source][1]
    root = cache/'upstream'/source
    for rel, meta in manifest['sources'][source]['files'].items():
        assert sha(root/rel) == meta['sha256'], f'Hash mismatch: {source}/{rel}'
    return root

def record(**kwargs):
    base = dict(item_id=None, source=None, construction=None, condition=None, sentence=None,
                question_type=None, question=None, gold=None, initial_parse_claim=None,
                final_parse_claim=None, ambiguity_start=None, disambiguator_index=None,
                cue_type=None, extension_length=0, source_row_id=None)
    base.update(kwargs)
    validate_record(base)
    return base

def validate_record(row):
    """Shared schema invariants, including genuinely absent source annotations."""
    required = ('item_id','source','construction','condition','sentence',
                'question_type','question','gold','initial_parse_claim',
                'final_parse_claim','ambiguity_start','disambiguator_index',
                'cue_type','extension_length','source_row_id')
    assert all(key in row for key in required)
    assert row['source'] in SOURCES
    for key in ('item_id','construction','condition','sentence','source_row_id'):
        assert isinstance(row[key],str) and row[key].strip(), (key,row[key])
    assert row['gold'] in (None,'Yes','No')
    for key in ('question_type','question','initial_parse_claim','final_parse_claim','cue_type'):
        assert row[key] is None or isinstance(row[key],str),key
    for key in ('ambiguity_start','disambiguator_index'):
        value=row[key]
        assert value is None or (type(value) is int and 0<=value<len(row['sentence'].split())),(key,value)
    assert type(row['extension_length']) is int and row['extension_length']>=0
    if row['gold'] is not None:
        assert row['question'] and row['question_type']

def amouyal(cache):
    root = verified_root(cache, 'amouyal')
    rows = read_table(root/'data/extended_gardenpath_experiments.csv')
    sets = collections.defaultdict(list)
    for r in rows:
        sets[r['set_id']].append(r)
    for sid, group in sets.items():
        assert len(group) == 4, sid
        assert {(r['sent_type'].startswith('nonGP'), r['quest_type']) for r in group} == {(c,q) for c in (False,True) for q in ('GP_question','simple_question')}
        for qt in ('GP_question', 'simple_question'):
            pair = [r for r in group if r['quest_type'] == qt]
            assert len({(r['question'],r['correct_answer']) for r in pair}) == 1
    result = []
    for i, r in enumerate(rows):
        group = sets[r['set_id']]
        initial = next(x['question'] for x in group if x['quest_type']=='GP_question')
        final = next(x['question'] for x in group if x['quest_type']=='simple_question')
        result.append(record(item_id=f'amouyal:{i}', source='amouyal', construction='NPZ',
            condition='non_gp' if r['sent_type'].startswith('nonGP') else 'gp',
            sentence=r['sentence'], question_type='lingering' if r['quest_type']=='GP_question' else 'simple',
            question=r['question'], gold=r['correct_answer'],
            initial_parse_claim=f'The answer to "{initial}" is Yes.',
            final_parse_claim=f'The answer to "{final}" is Yes.',
            source_row_id=r['Unnamed: 0'], pair_id=r['set_id'],
            upstream_sent_type=r['sent_type'], upstream_question_type=r['quest_type'],
            subtype=r['sent_type'].split('_',1)[1], position_status='not annotated upstream'))
    return result

def turing(cache):
    root = verified_root(cache, 'turing')
    result=[]
    for file in ('Christianson_2001.tsv','Alternates_2022.tsv'):
        for r in read_table(root/'data/external/garden_path'/file):
            result.append(record(item_id=f'turing:{file}:{r["Index"]}:{r["Label"]}', source='turing', construction='NPZ',
                condition='gp' if r['Label'] in ('OT','RAT') else 'explicit_cue', sentence=r['Sentence'],
                source_row_id=f'{file}:{r["Index"]}:{r["Label"]}', pair_id=f'{file}:{r["Index"]}',
                cue_type='comma' if r['Label'] in ('DOT','DRAT') else 'none', upstream_label=r['Label'],
                question_status='upstream grammaticality stimuli; comprehension gold not supplied'))
    return result

def write_jsonl(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=CACHE)
    ap.add_argument('--audit-out',type=Path);args=ap.parse_args()
    report=audit(args.cache)
    (args.cache/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    if args.audit_out:args.audit_out.write_text(json.dumps(report,indent=2)+'\n')
    for source,loader in [('amouyal',amouyal),('turing',turing)]:
        rows=loader(args.cache);write_jsonl(args.cache/'normalized'/f'{source}.jsonl',rows)
        print(source,len(rows),sha(args.cache/'normalized'/f'{source}.jsonl'))

if __name__=='__main__':main()
