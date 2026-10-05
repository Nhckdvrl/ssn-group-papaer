"""E14 cache-only, independently annotated event-reference transformations.

No semantic gold. The first sentence remains the author's exact expanded text;
only a reviewed bridge and the first literal S2 reference span are varied.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import numpy as np
from analyze import estimate
from data import CACHE, sha, write_jsonl, validate_record


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def build(cache, fields_path, out):
    rows = list(map(json.loads, (cache / 'normalized/slattery2013.jsonl').read_text().splitlines()))
    packets_path = fields_path.parent / 'extraction-packets.json'
    packets = json.loads(packets_path.read_text())
    assert packets['source_normalized_sha256'] == sha(cache / 'normalized/slattery2013.jsonl')
    packets = {p['pair_id']: p for p in packets['packets']}
    fields = json.loads(fields_path.read_text())
    annotations = {r['pair_id']: r for r in fields['rows']}
    assert len(annotations) == len(fields['rows']) == len(packets) == 22
    built = []
    for r in rows:
        if r['pair_id'] not in annotations:
            continue
        a = annotations[r['pair_id']]
        canonical = json.dumps(packets[r['pair_id']], sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        assert digest(canonical) == a['input_sha256']
        first, second = r['sentence'].split('. ', 1)
        first += '.'
        # A source subject inside an embedded clause can be lower-case, while
        # the bridge starts a sentence. Allow that initial capitalization only.
        assert a['S2_subject'] in second or a['S2_subject'][0].lower() + a['S2_subject'][1:] in second
        same, separate = a['same_event_bridge'], a['separate_event_bridge']
        assert same == f"{a['S2_subject']} continued that particular {a['event_noun_phrase']}."
        assert separate == f"{a['S2_subject']} began a separate {a['event_noun_phrase']}."
        assert len(same.split()) == len(separate.split())
        options = {p['source_np_option']: p for p in a['initial_patient_nps']}
        assert set(options) == {0, 1}
        p = options[r['source_np_option']]
        full_np = p['text']
        assert full_np in first and r['source_np_alternative'] in full_np
        # Keep the original determiner and premodifiers through the authored
        # alternative, without echoing the entire following relative clause.
        choice = re.search(r'(?<!\w)' + re.escape(r['source_np_alternative']) + r'(?!\w)', full_np)
        assert choice
        core_np = full_np[:choice.end()]
        assert core_np in first
        if 'core_text' in p:
            assert core_np == p['core_text']
        ref = re.search(r'\b(?:himself|herself|themselves|each other)\b', second)
        assert ref and ref.group() == r['literal_reference_text']
        for anchor, bridge in [('none', ''), ('same', same), ('separate', separate)]:
            context = first + ' ' + (bridge + ' ' if bridge else '')
            for target, phrase in [('source_reference', ref.group()), ('source_np', core_np)]:
                followup = second[:ref.start()] + phrase + second[ref.end():]
                text = context + followup
                start = len(context) + ref.start()
                stop = start + len(phrase)
                words = list(re.finditer(r'\S+', text))
                span = [i for i, w in enumerate(words) if w.start() < stop and w.end() > start]
                assert span and ' '.join(words[i].group() for i in span) == phrase
                item = {k: v for k, v in r.items() if k not in ('second_sentence_start_word',
                       'second_sentence_word_count', 'literal_reference_word_indices', 'literal_reference_text')}
                item.update(item_id=f"E14:{r['item_id']}:{anchor}:{target}", sentence=text,
                    source_item_id=r['item_id'], episode_anchor=anchor, target_kind=target,
                    source_sentence_sha256=digest(r['sentence']), first_sentence_sha256=digest(first),
                    bridge_sha256=digest(bridge), bridge_word_count=len(bridge.split()),
                    target_span_word_indices=span, target_start_char=start, target_stop_char=stop,
                    target_context_sha256=digest(text[:start]), target_phrase_sha256=digest(phrase),
                    authored_followup_start_word=len(context.split()),
                    annotation_fields_sha256=sha(fields_path), proposed_alignment_status=a['alignment_status'],
                    gold=None, gold_status='no_semantic_gold', question=None,
                    transformation='Source S1 unchanged; optional annotated same/separate bridge; first literal S2 reference optionally replaced by original core NP. No new questions.')
                validate_record(item)
                assert text.startswith(first + ' ')
                if anchor == 'none' and target == 'source_reference':
                    assert text == r['sentence']
                built.append(item)
    assert len(built) == 528 and len({r['item_id'] for r in built}) == 528
    assert not out.exists(), 'Immutable candidate version'
    write_jsonl(out, built)
    report = dict(source_items=22, candidates=528, source_normalized_sha256=sha(cache / 'normalized/slattery2013.jsonl'),
                  fields_sha256=sha(fields_path), candidates_sha256=sha(out),
                  generator_sha256=sha(Path(__file__)), source_reference_none_parity=88,
                  semantic_gold_labels=0, independent_final_review='pending', raw_in_git=False,
                  license='Derived from Slattery2013 publisher-copyright text; candidates stay cache-only.')
    out.with_suffix('.preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def adopt(data, reviews, out, scope_reviews=()):
    rows = list(map(json.loads, data.read_text().splitlines()))
    byid = {}
    for review_path in reviews:
        review = json.loads(review_path.read_text())
        assert review['model'] == 'gpt-6-luna'
        for r in review['variant_reviews']:
            assert r['item_id'] not in byid
            byid[r['item_id']] = (r, sha(review_path))
    assert set(byid) == {r['item_id'] for r in rows}, 'Incomplete independent variant review'
    scope = {}
    for path in scope_reviews:
        review = json.loads(path.read_text())
        assert review['model'] == 'gpt-6-luna'
        for a in review['source_reviews']:
            assert a['source_id'] not in scope
            assert a['followup_temporal_scope'] in ('episodic', 'generic_or_habitual', 'modal_or_dispositional', 'uncertain')
            assert a['source_followup_matches_original_activity'] in ('clear', 'related_but_different', 'uncertain')
            assert a['followup_links_to_inserted_activity'] in ('clear', 'weak', 'uncertain')
            scope[a['source_id']] = a
    assert set(scope) == {r['pair_id'] for r in rows}, 'Complete source-scope review required'
    selected = []
    for r in rows:
        a, review_sha = byid[r['item_id']]
        assert a['sentence_sha256'] == digest(r['sentence'])
        assert a['grammaticality'] in ('acceptable', 'marginal', 'unacceptable')
        assert a['reference_status'] in ('same', 'separate', 'none', 'uncertain')
        assert type(a['target_transformation_faithful']) is bool
        eligible = a['grammaticality'] != 'unacceptable' and a['target_transformation_faithful']
        # Ambiguous references are retained, with an independently defined clear
        # stratum for testing the referential interaction; no model scores used.
        s = scope[r['pair_id']]
        selected.append(dict(r, eligible=eligible,
                    clear_reference=eligible and a['reference_status'] == r['episode_anchor'],
                    episodic_reference=eligible and a['reference_status'] == r['episode_anchor'] and
                        s['followup_temporal_scope']=='episodic' and s['source_followup_matches_original_activity']=='clear' and
                        s['followup_links_to_inserted_activity']=='clear',
                    followup_temporal_scope=s['followup_temporal_scope'],
                    followup_activity_match=s['source_followup_matches_original_activity'],
                    followup_episode_link=s['followup_links_to_inserted_activity'],
                    audit_grammar=a['grammaticality'], audit_reference_status=a['reference_status'],
                    audit_event_identity_notes=a['reason'], audit_provider='gpt-6-luna',
                    audit_review_sha256=review_sha, sentence_sha256=digest(r['sentence'])))
    assert not out.exists()
    write_jsonl(out, selected)
    summary = dict(candidate_sha256=sha(data), audited_sha256=sha(out), variants=len(rows),
                   eligible=sum(r['eligible'] for r in selected),
                   clear_reference=sum(r['clear_reference'] for r in selected),
                   episodic_source_items=len({r['pair_id'] for r in selected if r['episodic_reference']}),
                   temporal_scope_counts=dict(collections.Counter(a['followup_temporal_scope'] for a in scope.values())),
                   scope_review_sha256=[sha(p) for p in scope_reviews],
                   grammar_counts=dict(collections.Counter(r['audit_grammar'] for r in selected)),
                   source_items=len({r['pair_id'] for r in selected}),
                   review_sha256=[sha(p) for p in reviews], semantic_gold_labels=0,
                   scope='Independent rendered-variant review; probability contrasts only, no human gold or internal event-graph claim.')
    out.with_suffix('.audit.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def analyze(path):
    cfg = json.loads((path / 'config.json').read_text())
    assert cfg['scores_sha256'] == sha(path / 'scores.jsonl')
    rows = list(map(json.loads, (path / 'scores.jsonl').read_text().splitlines()))
    assert len(rows) == cfg['task_count']
    result = dict(experiment='E14', primary='Same minus separate interaction in GP-minus-comma preference for source reference over source NP, in bits.',
                  units='Target NP-span total bits; positive reference preference = initial-NP surprisal minus source-reference surprisal.',
                  interpretation='Conditional continuation preference, not accuracy or proof of an internal event graph. Length differs between alternatives; within-source GP/cue comparisons cancel fixed lexical alternatives.',
                  cells={}, gp_minus_comma={}, anchor_interactions={}, paired_ids={},
                  bootstrap_seed=20261005, bootstrap_draws=10000, scores_sha256=cfg['scores_sha256'],
                  analysis_code_sha256=sha(Path(__file__)))
    def stat(v):
        if len(v) < 2:
            return dict(estimate=next(iter(v.values()), None), ci95=None, n_sets=len(v), pair_ids=sorted(v))
        return dict(estimate([v[k] for k in sorted(v)]), pair_ids=sorted(v))
    def diff(a, b):
        return {k: a[k] - b[k] for k in a.keys() & b.keys()}
    for stratum in ('eligible', 'clear_reference', 'episodic_reference'):
        for block in ('all22', 'first12', 'last12'):
            rr = [r for r in rows if r[stratum] and (block == 'all22' or r['source_block'] == block)]
            index = {(r['pair_id'], r['source_np_option'], r['condition'], r['episode_anchor'], r['target_kind']): r for r in rr}
            assert len(index) == len(rr)
            effects = {}
            for option in (0, 1, 'both'):
                def prefs(condition, anchor):
                    vals = {}
                    for sid in sorted({r['pair_id'] for r in rr}):
                        options = (0, 1) if option == 'both' else (option,)
                        scores = []
                        for o in options:
                            a = index.get((sid, o, condition, anchor, 'source_reference'))
                            b = index.get((sid, o, condition, anchor, 'source_np'))
                            if a is None or b is None:
                                break
                            assert a['target_context_sha256'] == b['target_context_sha256']
                            scores.append(b['target_total_bits'] - a['target_total_bits'])
                        if len(scores) == len(options):
                            vals[sid] = float(np.mean(scores))
                    return vals
                ds = {}
                for anchor in ('none', 'same', 'separate'):
                    vs = {c: prefs(c, anchor) for c in ('gp', 'explicit_cue')}
                    prefix = f'{stratum}/{block}/option{option}/{anchor}'
                    for c, v in vs.items():
                        result['cells'][prefix + '/' + c] = stat(v)
                    ds[anchor] = diff(vs['gp'], vs['explicit_cue'])
                    result['gp_minus_comma'][prefix] = stat(ds[anchor])
                for a, b in [('same', 'separate'), ('same', 'none'), ('separate', 'none')]:
                    result['anchor_interactions'][f'{stratum}/{block}/option{option}/{a}_minus_{b}'] = stat(diff(ds[a], ds[b]))
                effects[option] = ds
            # Both options must be available before treating a source as an
            # independently paired source-level primary observation.
            result['paired_ids'][f'{stratum}/{block}'] = sorted(effects['both']['same'].keys() & effects['both']['separate'].keys())
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='action', required=True)
    b = sub.add_parser('build'); b.add_argument('--fields', type=Path, required=True); b.add_argument('--out', type=Path, required=True)
    a = sub.add_parser('adopt'); a.add_argument('--data', type=Path, required=True); a.add_argument('--reviews', nargs='+', type=Path, required=True); a.add_argument('--scope-reviews', nargs='+', type=Path, required=True); a.add_argument('--out', type=Path, required=True)
    s = sub.add_parser('analyze'); s.add_argument('run_dir', type=Path); s.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    if args.action == 'build':
        print(json.dumps(build(CACHE, args.fields, args.out), indent=2))
    elif args.action == 'adopt':
        print(json.dumps(adopt(args.data, args.reviews, args.out, args.scope_reviews), indent=2))
    else:
        args.out.write_text(json.dumps(analyze(args.run_dir), indent=2) + '\n')
