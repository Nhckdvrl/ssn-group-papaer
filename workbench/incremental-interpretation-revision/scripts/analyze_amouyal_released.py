"""Audit of the publicly released Amouyal et al. (ACL 2025/2026) LLM and human results.

No new inference. Splits GP-question accuracy by item type, separating items whose
probed initial-parse proposition is false under the final parse (reflexive /
unaccusative NP/Z, reduced relative, NP/VP) from items where it is only "not
necessarily" true (optionally transitive NP/Z, many NP/S). Accuracy = share of
prompts where P(correct) > P(incorrect), regular (non-CoT, non-thinking) runs,
averaged over the released prompt suite. Usage:
  python3 analyze_amouyal_released.py --repo <clone of samsam3232/comparing_humans_llms_processing_difficulties> --out <json>
"""
import argparse, collections, csv, glob, json, sys
from pathlib import Path

TYPES = ['GP_prob', 'nonGP_prob', 'GP_reflexive', 'nonGP_reflexive', 'nps_gp', 'nps_nongp',
         'reduced_relative_gp', 'reduced_relative_nongp', 'npvp_gp', 'npvp_nongp']


def gp_question(st, q):
    if st in ('GP_prob', 'nonGP_prob', 'GP_reflexive', 'nonGP_reflexive'):
        return q == 'GP_question'
    if st.endswith(('_gp', '_nongp')):
        return q == 'gp_question'
    return False


def main(repo, out):
    csv.field_size_limit(sys.maxsize)
    acc = collections.defaultdict(list)
    missing = collections.Counter()
    for f in sorted(glob.glob(str(repo / 'results/llm_results/*.csv'))):
        for r in csv.DictReader(open(f)):
            if r['compute_type'] != 'regular' or r['sent_type'] not in TYPES or not gp_question(r['sent_type'], r['quest_type']):
                continue
            if not r['correct'] or not r['incorrect']:
                missing[r['model'].split('/')[-1]] += 1
                continue
            acc[(r['model'].split('/')[-1], r['sent_type'])].append(float(r['correct']) > float(r['incorrect']))
    human = collections.defaultdict(list)
    for r in csv.DictReader(open(repo / 'results/human_results/humans.csv')):
        if r['sent_type'] in TYPES and gp_question(r['sent_type'], r['quest_type']):
            human[r['sent_type']].append(r['correct'] in ('1', 'True', 'true', '1.0'))
    pct = lambda v: round(100 * sum(v) / len(v), 1) if v else None
    models = sorted({m for m, _ in acc})
    result = dict(
        source='samsam3232/comparing_humans_llms_processing_difficulties (released results, no new inference)',
        accuracy_definition='share of released prompts with P(correct) > P(incorrect); regular runs only; GP-targeted questions only',
        types=TYPES, human={t: pct(human[t]) for t in TYPES}, n_human={t: len(human[t]) for t in TYPES},
        models={m: {t: pct(acc[(m, t)]) for t in TYPES} for m in models},
        n_prompts={m: {t: len(acc[(m, t)]) for t in TYPES} for m in models},
        skipped_rows_with_empty_probabilities=dict(missing))
    out.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    main(a.repo, a.out)
