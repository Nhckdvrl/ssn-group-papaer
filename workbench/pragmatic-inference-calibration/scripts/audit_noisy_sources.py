"""E54 public-source audit; export only linguistic materials, never participant fields."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/data1/xiangding/work/pragmatic-inference-calibration')
ASSET = ROOT / 'parents/noisy-channel-osf-k5vqj'
OUT = Path(__file__).resolve().parents[1] / 'results/E54-noisy-source-audit-r2.json'


def read(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def file_info(p):
    return {'file': str(p.relative_to(ASSET)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def main():
    assert not OUT.exists()
    files = sorted((ASSET / 'data').glob('Experiment*.csv'))
    loaded = {p: read(p) for p in files}
    global_n = {}
    cross_file = []
    global_control_accuracy = {}
    for drop in (0, 2):
        grouped = defaultdict(list)
        for p, rows in loaded.items():
            for x in rows[drop:]:
                grouped[x['prolific_id']].extend((k,v) for k,v in x.items()
                    if re.fullmatch(r'list[1-4]\.(item|filler)\d+\.cond[^.]*\.literalResponse(Yes|No)',k) and v)
        global_n[drop] = {k:len(v) for k,v in grouped.items()}
        global_control_accuracy[drop] = {}
        for subject, vals in grouped.items():
            c = [(v == k.rsplit('literalResponse',1)[1]) for k,v in vals
                 if '.condfiller.' in k or re.search(r'\.cond[^.]+_plausible\.',k)]
            global_control_accuracy[drop][subject] = sum(c)/len(c) if c else 0
    for i,p in enumerate(files):
        x={r['prolific_id'] for r in loaded[p]}
        for q in files[i+1:]:
            overlap=len(x & {r['prolific_id'] for r in loaded[q]})
            cross_file.append({'file_a':p.name,'file_b':q.name,'duplicate_ids':overlap})
    qjep = []
    pattern = re.compile(r'^list[1-4]\.(item|filler)(\d+)\.cond([^.]*)\.literalResponse(Yes|No)$')
    for p in files:
        rows = loaded[p]
        fields = [k for k in rows[0] if pattern.fullmatch(k)]
        assert len(fields) == 320
        assert all(v in ('', 'Yes', 'No') for x in rows for k, v in x.items() if k in fields)
        # Published R removes two Qualtrics metadata rows; this release begins with responses.
        variants = []
        for drop in (0, 2):
            subjects = defaultdict(list)
            for x in rows[drop:]:
                values = [(k, x[k]) for k in fields if x[k]]
                subjects[x['prolific_id']].append((x, values))
            groups = defaultdict(list)
            kept = 0
            for trialsets in subjects.values():
                x = trialsets[0][0]
                vals = [v for _, vs in trialsets for v in vs]
                controls = [(v == pattern.fullmatch(k)[4]) for k, v in vals
                            if pattern.fullmatch(k)[1] == 'filler' or 'plausible' == pattern.fullmatch(k)[3].split('_')[-1]]
                accuracy = global_control_accuracy[drop][x['prolific_id']]
                if not (x['country'] == 'United States' and x['first_language'] == 'Yes'
                        and 72 <= global_n[drop][x['prolific_id']] <= 80 and accuracy >= .75):
                    continue
                kept += 1
                for k, v in vals:
                    m = pattern.fullmatch(k)
                    if m[3].endswith('_implausible'):
                        groups[m[3]].append(v == m[4])
            variants.append({'drop_first_rows': drop, 'retained_subjects': kept,
                             'conditions': {k: {'n': len(v), 'literal_rate': sum(v)/len(v)} for k, v in groups.items()}})
        qjep.append({**file_info(p), 'rows': len(rows), 'material_columns': len(fields),
                     'first_two_rows_are_responses': True, 'stimulus_text_missing': True,
                     'release_vs_code_variants': variants})

    gtp = []
    materials = {}
    all_sources = {}
    for p in sorted((ASSET / 'data/GTP2013data').glob('*.csv')):
        rows = read(p)
        critical = [x for x in rows if x['Condition'] != 'filler'
                    and not re.fullmatch(r'(active|passive)_v[12]', x['Condition'])]
        grouped = defaultdict(list)
        for x in critical:
            assert x['CorrectAnswer1'] in ('Yes', 'No')
            if x['Answer.YNQ1_'] in ('Yes', 'No'):
                assert x['Correct'] == str(x['Answer.YNQ1_'] == x['CorrectAnswer1']).upper()
                grouped[x['Condition']].append(x['Correct'] == 'TRUE')
        unique = {}
        for x in critical:
            key = (x['Item'], x['Condition'])
            material = {k: x[k] for k in ('Item', 'Condition', 'Input.trial_', 'Input.question_1_', 'CorrectAnswer1')}
            if key in unique:
                assert unique[key] == material
            unique[key] = material
        all_sources[p.name] = unique
        if re.match(r'^E[1-5]_', p.name):
            assert len(unique) == 80
            for key, v in unique.items():
                materials[p.name + ':' + '|'.join(key)] = {**v, 'source_file': p.name}
        gtp.append({**file_info(p), 'rows': len(rows), 'subjects': len({x['Participant'] for x in rows}),
                    'critical_unique': len(unique), 'conditions': {k: {'n': len(v), 'literal_rate': sum(v)/len(v)} for k,v in grouped.items()},
                    'critical_missing_response': sum(x['Answer.YNQ1_'] not in ('Yes','No') for x in critical)})
    matches = []
    for a, b in [('E1_loc_inversion_raw_data_2013.csv','E6_noise_locative_raw_data_2013.csv'),
                 ('E2_DOPOto_raw_data_2013.csv','E7_noise_DOPO_raw_data_2013.csv'),
                 ('E3_DOPOfor_raw_data_2013.csv','E8_noise_DOPO_for_raw_data_2013.csv'),
                 ('E4_active_passive_raw_data_2013.csv','E9_noise_active_passive_raw_data_2013.csv'),
                 ('E5_trans_intrans_raw_data_2013.csv','E10_noise_trans_intrans_raw_data_2013.csv')]:
        matches.append({'baseline': a, 'noise': b, 'identical_all_80_critical': all_sources[a] == all_sources[b]})
    assert len(materials) == 400
    material_path = ROOT / 'data/E54-original-critical-materials.json'
    material_text = json.dumps(list(materials.values()), indent=2)
    if material_path.exists():assert material_path.read_text()==material_text
    else:material_path.write_text(material_text)
    OUT.write_text(json.dumps({'qjep': qjep, 'gtp': gtp, 'baseline_noise_matches': matches,
        'cross_file_duplicate_ids':cross_file,'global_subject_filter_matches_R_groupby':True,
        'r1_per_file_subject_grouping_superseded':True,
        'no_gpu_predictions': True, 'export_contains_only_linguistic_fields': True,
        'qjep_original_script_directly_applicable': False,
        'human_exact_parity_not_yet_established': True}, indent=2)+'\n')
    print(json.dumps({'qjep_retained': [(x['file'],x['release_vs_code_variants']) for x in qjep],
                      'gtp_baseline_unique': len(materials),'all_critical_matches': all(x['identical_all_80_critical'] for x in matches)},indent=2))


if __name__ == '__main__':
    main()
