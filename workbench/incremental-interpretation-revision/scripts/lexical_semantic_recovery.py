"""E85 published Blott Appendix I extraction; no new semantic gold or audit."""
import argparse
import collections
import json
from pathlib import Path
import re
from data import sha
from data_v2 import digest
from current_open_baseline import REPAIR

CONDITIONS = ['coherent_unambiguous', 'coherent_ambiguous',
              'anomalous_unambiguous', 'anomalous_ambiguous']


def extract(pdf, out):
    import fitz
    assert sha(pdf) == '844420d9d1ee8c939c7c18953c9f38d99ca387c347d51381320f10e73362aabb'
    doc = fitz.open(pdf)
    table = {}; current = None
    for i in range(45, 50):
        words = doc[i].get_text('words')
        for word in sorted(words, key=lambda w: (round(w[1], 1), w[0])):
            x, y, _, _, text, *_ = word
            if y < 65 or y > 780 or i == 45 and y < 569:
                continue
            if x < 105 and text.isdigit():
                item = int(text)
                if not 1 <= item <= 48:
                    continue
                assert item not in table
                current = item
                table[item] = dict(item=item, nouns=[], frame=[], single=[], embedded=[], pages=[])
            elif current is not None:
                if 110 <= x < 185:
                    table[current]['nouns'].append(text)
                elif 185 <= x < 313:
                    table[current]['frame'].append(text)
                elif 313 <= x < 355 and re.fullmatch(r'[01]\.\d+', text):
                    table[current]['single'].append(text)
                elif 355 <= x < 415 and re.fullmatch(r'[01]\.\d+', text):
                    table[current]['embedded'].append(text)
                else:
                    continue
                table[current]['pages'].append(i + 1)
    assert set(table) == set(range(1, 49)), sorted(table)
    stimuli, rows = [], []
    for item, r in sorted(table.items()):
        nouns = [x.strip() for x in ' '.join(r['nouns']).split('/')]
        assert len(nouns) == 4 and all(nouns), (item, nouns)
        frame = re.sub(r'\s+', ' ', ' '.join(r['frame'])).strip()
        # Two words are broken without hyphens by the PDF column layout.
        raw_frame = frame
        if item == 21:
            assert frame.endswith('loud er.')
            frame = frame[:-8] + 'louder.'
        if item == 37:
            assert '/tha n the/' in frame
            frame = frame.replace('/tha n the/', '/than the/')
        assert frame.count('MAIN NOUN') == 1 and len(r['single']) == len(r['embedded']) == 1, r
        regions = [x.strip() for x in frame.split('/')]
        # Item23 has five ROI strings in the published table; retain it unchanged.
        assert regions[1] == 'MAIN NOUN' and len(regions) in [5, 6], (item, regions)
        base = dict(item=item, main_nouns=nouns, frame=frame, pdf_layout_frame=raw_frame, regions=regions,
            dominance_single=float(r['single'][0]), dominance_embedded=float(r['embedded'][0]),
            pdf_pages=sorted(set(r['pages'])))
        stimuli.append(base)
        for condition, noun in zip(CONDITIONS, nouns):
            sentence = ' '.join(regions).replace('MAIN NOUN', noun)
            # Remove only ROI delimiters and normalize layout whitespace; punctuation stays original.
            rows.append(dict(base, item_id=f'Blott2020:{item}:{condition}', cluster_id=f'Blott2020:{item}',
                source_unit=f'Blott2020:{item}:{condition}', construction='lexical', condition=condition,
                sentence=sentence, sentence_sha256=digest(sentence),
                grounded_gold='Yes' if condition.startswith('coherent') else 'No',
                question='Does this sentence make sense?'))
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'data-v1.jsonl'
    assert not path.exists()
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    (out / 'stimuli-v1.json').write_text(json.dumps(stimuli, ensure_ascii=False, indent=2) + '\n')
    (out / 'data-v1.manifest.json').write_text(json.dumps(dict(data_sha256=sha(path),
        source_pdf=str(pdf), source_pdf_sha256=sha(pdf), items=192, lexical_frames=48,
        gold_origin='Original four-condition coherence design; not logical entailment or word-sense annotation.',
        processing='Original noun substitution; PDF whitespace/ROI separators only; all 48 retained; no API.'), indent=2) + '\n')
    print('E85 extracted', len(rows), sha(path))


def prepare(rows, tok):
    tasks = []
    for r in rows:
        assert digest(r['sentence']) == r['sentence_sha256']
        for op in ['DIRECT', 'ONE_RECOVER']:
            for ro in ['words', 'letters']:
                for mp, shown in enumerate([['Yes', 'No'], ['No', 'Yes']]):
                    lead = 'Read this sentence carefully.' + (' ' + REPAIR if op == 'ONE_RECOVER' else '')
                    body = lead + '\nSentence:\n' + r['sentence']
                    body += '\n\nTask:\nJudge whether the sentence makes sense in ordinary language.\nQuestion:\n' + r['question']
                    body += '\n' + '\n'.join(f'{a}. {b}' for a, b in zip(['A', 'B'], shown))
                    body += '\nAnswer only ' + ('Yes or No.' if ro == 'words' else 'A or B.')
                    prompt = tok.apply_chat_template([dict(role='user', content=body)], tokenize=False,
                        add_generation_prompt=True, enable_thinking=False)
                    name = tok.name_or_path
                    if 'Qwen3.8' in name:
                        assert prompt.endswith('<think>\n\n</think>\n\n')
                    elif 'gemma-4' in name:
                        assert prompt.endswith('<|channel>thought\n<channel|>')
                    else:
                        assert prompt.endswith('[/INST]')
                    choices = shown if ro == 'words' else ['A', 'B']
                    seqs = [tok.encode(prompt + c, add_special_tokens=False) for c in choices]
                    common = 0
                    for pair in zip(*seqs):
                        if pair[0] != pair[1]:
                            break
                        common += 1
                    assert common > 0 and all(len(s) == common + 1 for s in seqs)
                    tasks.append(dict(row=r, operation=op, readout=ro, mapping=mp, prompt=prompt,
                        sequences=seqs, common=common, candidate_gold=shown.index(r['grounded_gold'])))
    return tasks


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pdf', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    extract(a.pdf, a.out)
