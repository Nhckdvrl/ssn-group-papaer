"""Cache-only transcription of published Slattery et al. (2013), Appendix B.

This expands the author's optional comma and two NP alternatives. It invents
neither follow-up text nor semantic gold; publisher text is not redistributed.
"""
import collections
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import fitz
from data import CACHE, record, sha, write_jsonl

PDF_SHA='c5289cc80095e3a83ffc4f189e51b36583cda3b7011786a327b57e919c1df5f2'
URL='https://faculty.wcas.northwestern.edu/myo507/Papers/SlatteryEtAL_GoodEnough_Published.pdf'


def load_published(cache=CACHE):
    pdf=cache/'papers/slattery2013.pdf'; assert sha(pdf)==PDF_SHA
    doc=fitz.open(pdf); page=doc[15]; mid=page.rect.width/2
    # Both columns begin below the running publication header. Without this
    # geometric crop the header is silently inserted into item 11's follow-up.
    left=page.get_text('text',clip=fitz.Rect(0,50,mid,page.rect.height),sort=True)
    right=page.get_text('text',clip=fitz.Rect(mid,50,page.rect.width,page.rect.height),sort=True)
    raw=left.split('Appendix B',1)[1].split('Items from Experiment 2',1)[1]+'\n'+right.split('References',1)[0]
    normalized=unicodedata.normalize('NFKC',raw)
    parts=re.split(r'(?m)^\s*(\d+)\.\s+',normalized)
    assert [int(i) for i in parts[1::2]]==list(range(1,25))
    templates=[(int(i),' '.join(t.split())) for i,t in zip(parts[1::2],parts[2::2])]
    rows=[]
    for i,template in templates:
        assert template.count('|,|')==1
        alternatives=re.findall(r'\|([^|]+/[^|]+)\|',template)
        assert len(alternatives)==1
        choices=[x.strip() for x in alternatives[0].split('/')]; assert len(choices)==2
        for option in (0,1):
            for condition in ('gp','explicit_cue'):
                text=template.replace('|,|',',' if condition=='explicit_cue' else '').replace('|'+alternatives[0]+'|',choices[option])
                assert '|' not in text and 'Slattery' not in text and 'Language 69' not in text
                first,second=text.split('. ',1);first+='.'
                assert second.endswith('.') and first and second
                second_start=len(first.split())
                match=re.search(r'\b(?:himself|herself|themselves|each other)\b',second)
                reference_words=[len(second[:match.start()].split())+second_start+j for j in range(len(match.group().split()))] if match else []
                rows.append(record(item_id=f'slattery2013:{i}:{option}:{condition}',source='slattery2013',
                    construction='NPZ',condition=condition,sentence=text,question_type='authored_followup_probability',
                    question=None,gold=None,source_row_id=f'AppendixB:{i}',pair_id=f'Slattery:{i}',cue_type='none' if condition=='gp' else 'comma',
                    source_np_option=option,source_np_alternative=choices[option],second_sentence_start_word=second_start,
                    second_sentence_word_count=len(second.split()),literal_reference_word_indices=reference_words,
                    literal_reference_text=match.group() if match else None,
                    source_template_sha256=hashlib.sha256(template.encode()).hexdigest(),
                    source_revision_pdf_sha256=PDF_SHA,gold_status='no_semantic_gold',
                    source_block='first12' if i<=12 else 'last12',
                    annotation_scope='Original published two-sentence items; only author comma/NP alternatives expanded. Literal reference indices from exact string regex, not a semantic judgment.'))
    assert len(rows)==96 and len({r['item_id'] for r in rows})==96
    grouped=collections.defaultdict(list)
    for r in rows:grouped[r['pair_id']].append(r)
    for rr in grouped.values():
        assert len({r['sentence'].split('. ',1)[1] for r in rr})==1,'Follow-up changed across conditions'
    report=dict(url=URL,revision_pdf_sha256=PDF_SHA,pages=len(doc),article='Slattery et al. 2013, JML 69:104–120, Experiment 2 Appendix B',
                license='Publisher copyright ©2013 Elsevier Inc. All rights reserved. Public author-institution copy; no open redistribution license verified.',
                raw_in_git=False,redistribution='Original text and normalized stimuli remain local cache only; publish code, numeric statistics and citation.',
                proxy_used=False,new_download_bytes=0,templates=24,sentence_variants=96,
                followup_equal_in_all_four_author_variants=True,
                literal_reference_present_templates=sum(bool(rr[0]['literal_reference_word_indices']) for rr in grouped.values()),
                literal_reference_absent_source_ids=[s for s,rr in grouped.items() if not rr[0]['literal_reference_word_indices']],
                normalization='PDF columns cropped below y=50pt; NFKC converts typographic ligatures; whitespace collapsed; no spelling/word replacement beyond author NP alternatives and optional comma.',
                extraction_code_sha256=sha(Path(__file__)))
    return rows,report


if __name__=='__main__':
    rows,report=load_published()
    out=CACHE/'normalized/slattery2013.jsonl';assert not out.exists(),'Immutable source version'
    write_jsonl(out,rows);report['normalized_sha256']=sha(out)
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
