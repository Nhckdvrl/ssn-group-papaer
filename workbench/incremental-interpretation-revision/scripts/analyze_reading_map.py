"""E52 paired cluster-bootstrap map. Missing evidence never becomes a zero result."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import sha, write_jsonl


def load(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def assemble(data, annotation, out):
    rows = load(data); labels = {r['item_id']: r for r in load(annotation)}
    pass_paths=[annotation.parent/f'pass{n}.jsonl' for n in (1,2)]
    if all(p.exists() for p in pass_paths):
        passes=[{a['item_id']:a for a in load(p)} for p in pass_paths]
        for uid in passes[0].keys()&passes[1].keys():
            a,b=passes[0][uid],passes[1][uid]
            labels[uid].update(step5_passes=[a,b],step5_grammar_agreed=a['grammar']==b['grammar'],
                step5_position_agreed=(a['disamb_word_index'],a['amb_span'])==(b['disamb_word_index'],b['amb_span']))
    for row in rows:
        row['source_disamb_word_index']=row['disamb_word_index']
        row['disamb_word_index']=None
        row['amb_span']=None
        # Keep the immutable inference input, but correct analysis metadata for the
        # two polarity-matched depth-charge pairs instead of pooling three controls.
        row['analysis_pair_id'] = row['pair_id']
        row['analysis_condition'] = row['condition']
        row['analysis_question_target'] = row['question_target']
        if row['source'] == 'cehakova2025':
            row['analysis_question_target'] = 'initial' if row['source_question_type'].startswith('amb') else 'final'
        if row['source'] == 'amouyal' and row['construction'] == 'DEPTH':
            typ = row['source_sent_type']
            row['analysis_pair_id'] += ':inverse' if typ.startswith('inv_') else ':regular'
            row['analysis_condition'] = 'control' if typ.endswith('_baseline') else 'gp'
        annotated = labels.get(row['item_id'])
        if annotated:
            assert annotated['sentence_sha256'] == row['sentence_sha256']
            row.update({k: v for k, v in annotated.items() if k.startswith('step5_')})
    paired = collections.defaultdict(list)
    for row in rows:
        paired[(row['analysis_pair_id'], row['question'])].append(row)
    for key, group in paired.items():
        conditions = {r['analysis_condition'] for r in group}
        for row in group:
            row['genuine'] = False
            row['semantic_stratum'] = 'published_nonrevision_control' if not row['needs_revision'] else 'unresolved'
            if row.get('step5_status') not in ('agreed', 'adjudicated'): continue
            a = row['step5_annotation']
            if row['question_format'] == 'yn':
                row['semantic_stratum'] = a['label']
            else:
                row['semantic_stratum'] = 'ENTAILED_CHOICE' if a['option_labels'][row['gold']] == 'ENTAILED' else 'UNCERTAIN_CHOICE'
            others = [r for r in group if r['analysis_condition'] != row['analysis_condition']]
            if not row['needs_revision'] or row['analysis_question_target'] != 'initial' or conditions != {'gp', 'control'} or not others: continue
            candidate = [row, *others]
            if any(r.get('step5_status') not in ('agreed', 'adjudicated') for r in candidate): continue
            if any(not r.get('step5_grammar_agreed') or r['step5_annotation']['grammar'] != 'acceptable' or
                any(a['grammar']!='acceptable' for a in r['step5_passes']) for r in candidate): continue
            def contradicted(r):
                annotation = r['step5_annotation']
                if r['question_format'] == 'yn': return annotation['label'] == 'CONTRADICTED' and r['options'][r['gold']] == 'No'
                return annotation['option_labels'][r['gold']] == 'ENTAILED' and annotation['option_labels'][1-r['gold']] == 'CONTRADICTED'
            row['genuine'] = all(contradicted(r) for r in candidate)
    # Align a control landmark to the GP's independently labelled word, not to an invented control ambiguity.
    for group in paired.values():
        gps = [r for r in group if r['condition'] == 'gp' and r.get('step5_status') in ('agreed', 'adjudicated')]
        if not gps: continue
        gp = gps[0]; a = gp['step5_passes'][0]
        if not gp.get('step5_position_agreed'): continue
        adjudicated=gp['step5_annotation']
        if (adjudicated['disamb_word_index'],adjudicated['amb_span'])!=(a['disamb_word_index'],a['amb_span']):continue
        index = a['disamb_word_index']; word = a['disamb_word']
        if index is None: continue
        gp.update(disamb_word_index=index, amb_span=a['amb_span'], position_origin='two-pass Step5 agreement')
        for r in group:
            if r['condition'] != 'control': continue
            positions = [i for i, token in enumerate(r['sentence'].split()) if token.strip('.,;:').lower() == word.strip('.,;:').lower()]
            if len(positions) == 1:
                r.update(disamb_word_index=positions[0], position_origin='unique control word aligned to Step5 GP landmark')
    accepted_positions=collections.defaultdict(set)
    for r in rows:
        if r['condition']=='gp' and r.get('position_origin')=='two-pass Step5 agreement':
            accepted_positions[r['sentence_sha256']].add(r['disamb_word_index'])
    inconsistent={s for s,positions in accepted_positions.items() if len(positions)>1}
    for group in paired.values():
        if any(r['condition']=='gp' and r['sentence_sha256'] in inconsistent for r in group):
            for r in group:
                r.update(disamb_word_index=None,amb_span=None,position_origin='Step5 landmark inconsistent across questions for the same sentence')
    write_jsonl(out, rows)
    summary = dict(rows=len(rows), labelled=sum(r.get('step5_status') in ('agreed', 'adjudicated') for r in rows),
        genuine_pairs=len({r['pair_id'] for r in rows if r['genuine']}),
        semantic_strata=dict(collections.Counter(r['semantic_stratum'] for r in rows)),
        position_available=sum(r['disamb_word_index'] is not None for r in rows), data_sha256=sha(data),
        position_inconsistent_sentences=len(inconsistent),
        annotation_sha256=sha(annotation), assembled_sha256=sha(out))
    summary['pass_sha256']={p.name:sha(p) for p in pass_paths if p.exists()}
    out.with_suffix('.manifest.json').write_text(json.dumps(summary, indent=2)+'\n'); print(json.dumps(summary))


def estimate(values, seed=52):
    if not values: return dict(estimate=None, ci95=None, n_clusters=0)
    x = np.asarray([values[k] for k in sorted(values)], dtype=float)
    if len(x) == 1: return dict(estimate=float(x[0]), ci95=None, n_clusters=1)
    if np.all(x == x[0]): return dict(estimate=float(x[0]), ci95=[float(x[0]),float(x[0])], n_clusters=len(x))
    rng = np.random.default_rng(seed); means = []
    for _ in range(100): means.extend(x[rng.integers(0, len(x), size=(100, len(x)))].mean(1))
    return dict(estimate=float(x.mean()), ci95=list(map(float, np.quantile(means, [.025, .975]))), n_clusters=len(x))


def analyze(data, run_dirs, out, filler_audits=None, final_choice_audits=None):
    metadata = {r['item_id']: r for r in load(data)}; output = dict(models={}, data_sha256=sha(data), runs=[])
    per_model = collections.defaultdict(dict)
    identities = {}
    final_labels={};final_scopes=[];final_review_counts=collections.Counter()
    for directory in final_choice_audits or []:
        assert (directory/'step5/summary.json').exists(),'Incomplete final-choice audit'
        for r in load(directory/'step5/annotated.jsonl'):
            assert r['item_id'] not in final_labels,'Duplicate final-answer audit; never select favorable versions'
            final_labels[r['item_id']]=r
        final_scopes.append(dict(path=str(directory),scope=json.loads((directory/'scope.json').read_text()),
            annotation_sha256=sha(directory/'step5/annotated.jsonl')))
    filler_labels={};filler_scopes=[];filler_rejections=collections.Counter()
    for directory in filler_audits or []:
        scope=json.loads((directory/'scope.json').read_text())
        step=directory/'step5'
        assert (step/'summary.json').exists(),'Incomplete filler audit'
        for r in load(step/'annotated.jsonl'):
            assert r['sentence_sha256'] not in filler_labels,'Do not choose among duplicate filler audit versions'
            filler_labels[r['sentence_sha256']]=r
        filler_scopes.append(dict(path=str(directory),scope=scope,annotation_sha256=sha(step/'annotated.jsonl')))
    for directory in run_dirs:
        config = json.loads((directory/'config.json').read_text())
        assert config.get('predictions_sha256') == sha(directory/'predictions.jsonl'), 'Incomplete or modified run'
        predictions = load(directory/'predictions.jsonl'); model = Path(config['model_path']).name
        identity = config['model_manifest_sha256'], config['arguments']['dtype']
        assert identities.setdefault(model, identity) == identity, 'Do not merge different model bytes/precisions'
        output['runs'].append(dict(path=str(directory), config_sha256=sha(directory/'config.json')))
        for r in predictions:
            assert r['mode'] in ('sequence', 'generation'), 'Legacy processed scores are instrument calibration, not primary map'
            assert metadata[r['item_id']]['sentence_sha256'] == r['sentence_sha256']
            if r['mode']=='generation' and r['answer_status'] not in ('complete','complete_labelled_option','unfinished_thinking'):
                uid=f'{model}:{r["reading"]}:{r["item_id"]}:mapping{r["mapping"]}'
                audit=final_labels.get(uid)
                if audit is not None:
                    text=r['text'].rsplit('</think>',1)[1] if r['reading']=='R6' else r['text']
                    assert __import__('hashlib').sha256(text.encode()).hexdigest()==audit['sentence_sha256']
                    if audit.get('step5_status') in ('agreed','adjudicated'):
                        labels=audit['step5_annotation']['option_labels']
                        if labels in (['ENTAILED','CONTRADICTED'],['CONTRADICTED','ENTAILED']):
                            choice=labels.index('ENTAILED')
                            r.update(correct=choice==r['candidate_gold'],answer_status='Step5_validated_final_choice')
                            final_review_counts[model+'/resolved']+=1
                        else:final_review_counts[model+'/ambiguous']+=1
                    else:final_review_counts[model+'/unresolved_audit']+=1
                else:final_review_counts[model+'/not_audited']+=1
            if r['reading']=='R4' and metadata[r['item_id']].get('analysis_condition',r['condition'])=='gp':
                continue  # Original coarse DEPTH labels did not define a cue manipulation.
            if r['reading']=='R3':
                assert filler_labels,'R3 inference needs independent filler quality audit before interpretation'
                sentence=metadata[r['item_id']]['sentence']
                matches=[f for f in filler_labels.values() if f['sentence']+'\n'+sentence in r['prompt']]
                assert len(matches)==1,'Missing or ambiguous audited filler; audit all distinct actual fillers first'
                filler=matches[0]
                accepted=(filler.get('step5_status') in ('agreed','adjudicated') and filler.get('step5_grammar_agreed') and
                    filler['step5_annotation']['grammar']=='acceptable' and all(a['disamb_word_index'] is None for a in filler['step5_passes']))
                if not accepted:
                    filler_rejections[model]+=1;continue
            key = tuple(r[k] for k in ('item_id', 'format', 'reading', 'order', 'prompt_index', 'mapping', 'repair'))
            assert key not in per_model[model], 'Duplicate inference task; do not pick favorable runs'
            per_model[model][key] = r
    paired_metadata = collections.defaultdict(list)
    for m in metadata.values(): paired_metadata[(m.get('analysis_pair_id', m['pair_id']), m['question'])].append(m)
    effects=[]
    for model, keyed in per_model.items():
        predictions = list(keyed.values())
        for construction in sorted({r['construction'] for r in predictions} | {'pooled'}):
            for fmt in ('A', 'B'):
                selected = [r for r in predictions if r['format'] == fmt and (construction == 'pooled' or r['construction'] == construction)]
                for stratum in ('genuine', 'NEITHER', 'initial_all', 'final', 'nonrevision'):
                    def eligible(r):
                        m = metadata[r['item_id']]
                        if stratum == 'genuine': return m['genuine']
                        target = m.get('analysis_question_target', m['question_target'])
                        if stratum == 'NEITHER': return target == 'initial' and m['semantic_stratum'] == 'NEITHER'
                        if stratum == 'initial_all': return target == 'initial'
                        if stratum == 'final': return target == 'final'
                        return not m['needs_revision']
                    eligible_ids = {r['item_id'] for r in selected if eligible(r)}
                    # Require both sides of the SAME question to be in the stratum.
                    # A GP NEITHER item cannot borrow a different control question.
                    pairs = {k: g for k, g in paired_metadata.items() if
                        {m.get('analysis_condition', m['condition']) for m in g if m['item_id'] in eligible_ids} == {'gp', 'control'}}
                    subset = [r for r in selected if r['item_id'] in eligible_ids and r['correct'] is not None and not r['repair'] and
                        (metadata[r['item_id']].get('analysis_pair_id', r['pair_id']), metadata[r['item_id']]['question']) in pairs]
                    for metric in ('correct', 'p_correct'):
                        # Keep question-pair identity until computing each contrast,
                        # then average questions inside the lexical cluster.
                        items = collections.defaultdict(list)
                        for r in subset:
                            if not r['matched_question_exact']: continue
                            if r[metric] is None: continue  # Generated final answers have no candidate probability.
                            m = metadata[r['item_id']]
                            qkey = m.get('analysis_pair_id', r['pair_id']), m['question']
                            items[(r['reading'], m.get('analysis_condition', r['condition']), r['cluster_id'], qkey, r['item_id'])].append(float(r[metric]))
                        question_cells = collections.defaultdict(lambda: collections.defaultdict(list))
                        for (reading, condition, cluster, question, item), scores in items.items():
                            question_cells[(reading, condition)][(cluster, question)].append(np.mean(scores))
                        question_cells = {k: {q: float(np.mean(scores)) for q, scores in v.items()} for k, v in question_cells.items()}
                        def cluster_mean(values):
                            groups = collections.defaultdict(list)
                            for (cluster, question), value in values.items(): groups[cluster].append(value)
                            return {k: float(np.mean(v)) for k, v in groups.items()}
                        cells = {k: cluster_mean(v) for k, v in question_cells.items()}
                        gaps = {}
                        for reading in sorted({k[0] for k in cells}):
                            gp, control = question_cells.get((reading, 'gp'), {}), question_cells.get((reading, 'control'), {})
                            common = gp.keys() & control.keys(); gaps[reading] = {k: control[k]-gp[k] for k in common}
                        key = f'{construction}/{fmt}/{stratum}/{metric}'
                        def summarize(values, statistic):
                            effects.extend(dict(model=model,construction=construction,format=fmt,stratum=stratum,metric=metric,
                                statistic=statistic,cluster_id=cluster,value=value) for cluster,value in values.items())
                            return estimate(values)
                        report = dict(cells={f'{k[0]}/{k[1]}': summarize(v,f'cell/{k[0]}/{k[1]}') for k, v in cells.items()},
                                      gaps={k: summarize(cluster_mean(v),f'gap/{k}') for k, v in gaps.items()}, reductions={}, raw_gains={})
                        for reading, gap in gaps.items():
                            if reading == 'R0': continue
                            base = gaps.get('R0', {}); common = base.keys() & gap.keys()
                            report['reductions'][reading] = summarize(cluster_mean({k: base[k]-gap[k] for k in common}),f'reduction/{reading}')
                            report['raw_gains'][reading] = {}
                            for condition in ('gp', 'control'):
                                a, b = question_cells.get(('R0', condition), {}), question_cells.get((reading, condition), {})
                                common = a.keys() & b.keys()
                                report['raw_gains'][reading][condition] = summarize(cluster_mean({k: b[k]-a[k] for k in common}),f'gain/{reading}/{condition}')
                        report['R1_vs_controls'] = {}
                        for reading in ('R2', 'R3'):
                            a, b = gaps.get('R1', {}), gaps.get(reading, {}); common = a.keys() & b.keys()
                            report['R1_vs_controls'][reading] = summarize(cluster_mean({k: b[k]-a[k] for k in common}),f'R1_vs/{reading}')
                        # R8: report the one-instruction recovery separately, not discarded.
                        repair_items=collections.defaultdict(list)
                        for r in selected:
                            if r['item_id'] not in eligible_ids or r['reading']!='R0' or not r['matched_question_exact'] or r[metric] is None: continue
                            m=metadata[r['item_id']];qkey=m.get('analysis_pair_id',r['pair_id']),m['question']
                            if qkey not in pairs:continue
                            repair_items[(bool(r['repair']),m.get('analysis_condition',r['condition']),r['cluster_id'],qkey,r['item_id'])].append(float(r[metric]))
                        repair_cells=collections.defaultdict(lambda:collections.defaultdict(list))
                        for (repair,condition,cluster,qkey,item),values in repair_items.items():repair_cells[(repair,condition)][(cluster,qkey)].append(np.mean(values))
                        repair_cells={k:{q:float(np.mean(v)) for q,v in values.items()} for k,values in repair_cells.items()}
                        report['instruction_recovery']={}
                        gains={}
                        for condition in ('gp','control'):
                            a,b=repair_cells.get((False,condition),{}),repair_cells.get((True,condition),{})
                            common=a.keys()&b.keys();gains[condition]={k:b[k]-a[k] for k in common}
                            report['instruction_recovery'][condition]=summarize(cluster_mean(gains[condition]),f'instruction_gain/{condition}')
                        common=gains['gp'].keys()&gains['control'].keys()
                        report['instruction_recovery']['selective_gain']=summarize(cluster_mean({k:gains['gp'][k]-gains['control'][k] for k in common}),'instruction_selective_gain')
                        report['thinking_vs_matched_generation']={}
                        a,b=gaps.get('R0-generation',{}),gaps.get('R6',{})
                        common=a.keys()&b.keys()
                        report['thinking_vs_matched_generation']['gap_reduction']=summarize(cluster_mean({k:a[k]-b[k] for k in common}),'thinking_matched_reduction')
                        output['models'].setdefault(model, {})[key] = report
    effects_path=out.with_suffix('.cluster-effects.jsonl');write_jsonl(effects_path,effects)
    output['cluster_effects_path']=str(effects_path);output['cluster_effects_sha256']=sha(effects_path)
    output['filler_audits']=filler_scopes;output['filler_quality_excluded_tasks']=dict(filler_rejections)
    output['final_choice_audits']=final_scopes;output['final_choice_review_counts']=dict(final_review_counts)
    output['interpretation'] = 'NEITHER/initial_all are agreement with the published No convention, not semantic accuracy. No automatic scientific account selection.'
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--annotation', type=Path); ap.add_argument('--runs', type=Path, nargs='*')
    ap.add_argument('--filler-audits',type=Path,nargs='*')
    ap.add_argument('--final-choice-audits',type=Path,nargs='*')
    ap.add_argument('--out', type=Path, required=True); args = ap.parse_args()
    if args.annotation: assemble(args.data, args.annotation, args.out)
    else: analyze(args.data, args.runs, args.out,args.filler_audits,args.final_choice_audits)
