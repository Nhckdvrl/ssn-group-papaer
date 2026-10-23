"""Assistant-only token spans for the fixed Qwen3 ChatML serialization."""
import re


def assistant_token_spans(rendered, roles, offsets):
    blocks=list(re.finditer(r'<\|im_start\|>(system|user|assistant)\n(.*?)<\|im_end\|>',rendered,re.S))
    if [m.group(1) for m in blocks]!=roles:
        raise ValueError('Serialized roles differ from source; no silent target masking')
    spans=[]
    for block in blocks:
        if block.group(1)!='assistant':continue
        begin,end=block.start(2),block.end()
        # The non-thinking Qwen3 prefix is supplied before generation, just as
        # in the original single-turn cache; do not count it as source supervision.
        empty_think='<think>\n\n</think>\n\n'
        if block.group(2).startswith(empty_think):begin+=len(empty_think)
        indices=[i for i,(a,b) in enumerate(offsets) if b>begin and a<end]
        if not indices or indices[0]==0 or indices!=list(range(indices[0],indices[-1]+1)):
            raise ValueError('Unusable assistant token interval')
        spans.append([indices[0],indices[-1]+1])
    if not spans:raise ValueError('No assistant targets')
    return spans


def target_positions(length,prompt_length,spans=None):
    if spans is None:spans=[[prompt_length,length]]
    positions=[];previous=0
    for begin,end in spans:
        if not 0<begin<end<=length or begin<previous:raise ValueError('Invalid target span')
        positions.extend(range(begin,end));previous=end
    if not positions:raise ValueError('Empty target')
    return positions
