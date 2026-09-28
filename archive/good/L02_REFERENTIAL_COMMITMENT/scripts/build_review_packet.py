"""Create a source-grounded review packet; no new gold labels."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/E000_20260908_v1'
rows = {r['id']: r for r in map(json.loads, (RUN / 'observations.jsonl').read_text().splitlines())}
doc = json.loads((RUN / 'documents.jsonl').read_text())
ss = doc['sentences']
notes = json.loads((ROOT / 'experiments/E000_data_audit/source_review.json').read_text())
protocol = json.loads((RUN / 'protocol.json').read_text())
xml = ET.parse(ROOT / protocol['source']).getroot()
fe_index = {fe.attrib['id']: fe for fe in xml.findall('./body/s/sem/frames/frame/fe')}
packet = []
for note in notes['items']:
    row = rows[note['id']]
    assert row['interpretation'] == 'INI' and row['source_link_present']
    chosen = {s['id'] for s in ss[max(0, row['sentence_index']-2):row['sentence_index']+3]}
    chosen.update(row['source_link']['sentence_ids'])
    packet.append({'observation': row, 'review': note,
                   'source_context': [{'id': s['id'], 'text': s['text']} for s in ss if s['id'] in chosen],
                   'source_fe_xml': ET.tostring(fe_index[row['id']], encoding='unicode')})
assert len(packet) == sum(r['interpretation'] == 'INI' and r['source_link_present'] for r in rows.values())
out = ROOT / 'experiments/E000_data_audit/review_packet.json'
content = json.dumps(packet, ensure_ascii=False, indent=2) + '\n'
if out.exists() and out.read_text() != content:
    raise ValueError('Existing review packet differs; use a versioned path')
out.write_text(content)
print(f'Verified source-grounded packet: {len(packet)} records')
