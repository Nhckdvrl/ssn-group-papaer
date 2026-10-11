"""Lossless NI inventory for the original SemEval-2010 Task 10 SALSA release.

Interpretation flags and source links are independent fields. This module never
infers semantic unanswerability from an INI flag or from missing annotation.
"""
from collections import Counter
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET

AUXILIARY = {'Coreference', 'Support', 'Relativization'}
INTERPRETATIONS = {'Definite_Interpretation': 'DNI', 'Indefinite_Interpretation': 'INI'}


class Corpus:
    def __init__(self, path):
        self.path = Path(path)
        self.sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.root = ET.parse(self.path).getroot()
        self.sentences = self.root.findall('./body/s')
        self.nodes, self.positions, self.node_sentence = {}, {}, {}
        self.parts = {}
        self.sentence_text = {}
        for si, sentence in enumerate(self.sentences):
            sid = sentence.attrib['id']
            terminals = sentence.findall('./graph/terminals/t')
            self.sentence_text[sid] = ' '.join(t.attrib['word'] for t in terminals)
            for ti, terminal in enumerate(terminals):
                self.positions[terminal.attrib['id']] = (si, ti, -1)
            for sw in sentence.findall('./sem/splitwords/splitword'):
                for pi, part in enumerate(sw.findall('part')):
                    self.parts[part.attrib['id']] = sw.attrib['idref']
                    self.positions[part.attrib['id']] = (*self.positions[sw.attrib['idref']][:2], pi)
            for node in sentence.iter():
                if node.tag not in {'t', 'nt', 'part'}:
                    continue
                nid = node.attrib['id']
                if nid in self.nodes:
                    raise ValueError(f'Duplicate node ID: {nid}')
                self.nodes[nid] = node
                self.node_sentence[nid] = sid

    def leaves(self, nid, active=()):
        if nid in active:
            raise ValueError(f'Graph cycle: {active} -> {nid}')
        if nid not in self.nodes:
            raise ValueError(f'Missing graph node: {nid}')
        node = self.nodes[nid]
        if node.tag in {'t', 'part'}:
            return [nid]
        leaves = [leaf for edge in node.findall('edge')
                  for leaf in self.leaves(edge.attrib['idref'], (*active, nid))]
        if not leaves:
            raise ValueError(f'Empty nonterminal: {nid}')
        return sorted(set(leaves), key=self.positions.__getitem__)

    def span(self, refs):
        leaves = sorted({leaf for ref in refs for leaf in self.leaves(ref)},
                        key=self.positions.__getitem__)
        return {'node_ids': refs, 'leaf_ids': leaves,
                'text': ' '.join(self.nodes[n].attrib['word'] for n in leaves),
                'sentence_ids': list(dict.fromkeys(self.node_sentence[n] for n in leaves)),
                'heads_as_released': [self.nodes[n].get('head') for n in refs]}

    def inventory(self):
        records, issues = [], []
        frame_counts = Counter()
        for si, sentence in enumerate(self.sentences):
            for frame in sentence.findall('./sem/frames/frame'):
                if frame.attrib['name'] in AUXILIARY:
                    continue
                frame_counts[frame.attrib['name']] += 1
                for fe in frame.findall('fe'):
                    flags = sorted(f.attrib['name'] for f in fe.findall('flag'))
                    labels = [INTERPRETATIONS[f] for f in flags if f in INTERPRETATIONS]
                    if not labels:
                        continue
                    refs = [n.attrib['idref'] for n in fe.findall('fenode')]
                    target_refs = [n.attrib['idref'] for n in frame.findall('./target/fenode')]
                    row = {'id': fe.attrib['id'], 'document_id': 'TigerOfSanPedro',
                           'source_split': 'train', 'source_sha256': self.sha256,
                           'sentence_id': sentence.attrib['id'], 'sentence_index': si,
                           'frame_id': frame.attrib['id'], 'frame': frame.attrib['name'],
                           'role': fe.attrib['name'], 'flags': flags,
                           'interpretation': labels[0] if len(labels) == 1 else 'CONFLICT',
                           'source_link_present': bool(refs),
                           'source_link_node_ids': refs, 'target_node_ids': target_refs,
                           'specific_filler_licensed': None,
                           'specific_filler_licensed_note': 'Not derived from interpretation or missing links',
                           'sentence_text_tokenized': self.sentence_text[sentence.attrib['id']]}
                    try:
                        row['target'] = self.span(target_refs)
                        row['source_link'] = self.span(refs)
                        row['link_sentence_offsets'] = sorted({self.positions[n][0] - si
                                                              for n in row['source_link']['leaf_ids']})
                        row['integrity'] = 'OK'
                    except ValueError as error:
                        row['integrity'] = 'UNRESOLVED'
                        issues.append({'id': row['id'], 'error': str(error)})
                    if len(labels) != 1:
                        issues.append({'id': row['id'], 'error': 'Conflicting interpretation flags'})
                    row['audit_flags'] = []
                    if row['interpretation'] == 'INI' and refs:
                        row['audit_flags'].append('INI_WITH_SOURCE_LINK')
                    if row['interpretation'] == 'DNI' and not refs:
                        row['audit_flags'].append('DNI_WITHOUT_SOURCE_LINK')
                    row['audit_flags'] += [f for f in flags if f.startswith('Uncertain_') or f == 'Global_reexamine']
                    records.append(row)
        ids = [r['id'] for r in records]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate NI IDs')
        return records, issues, frame_counts

    def graph_audit(self):
        issues = []
        for nid, node in self.nodes.items():
            if node.tag == 'nt':
                try:
                    self.leaves(nid)
                except ValueError as error:
                    issues.append({'node_id': nid, 'error': str(error)})
        for sentence in self.sentences:
            for fn in sentence.findall('./sem/frames/frame//fenode'):
                if fn.attrib['idref'] not in self.nodes:
                    issues.append({'sentence_id': sentence.attrib['id'],
                                   'missing_fenode': fn.attrib['idref']})
        return issues

    def documents(self):
        return {'document_id': 'TigerOfSanPedro', 'source_split': 'train',
                'source_sha256': self.sha256, 'rendering': 'Original terminal words joined with spaces; not detokenized',
                'sentences': [{'id': s.attrib['id'], 'index': i,
                               'tokens': [dict(t.attrib) for t in s.findall('./graph/terminals/t')],
                               'text': self.sentence_text[s.attrib['id']]}
                              for i, s in enumerate(self.sentences)]}
