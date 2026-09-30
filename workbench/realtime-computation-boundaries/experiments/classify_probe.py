"""Classify frontend behaviour in delegation probes: delegate_ok / delegate_degenerate / announce_no_handoff / answer_directly / refuse / silent."""
import collections, json, re, sys
def cls(x):
    if x['delegates']:
        return 'delegate_degenerate' if '<delegate>' in x['delegates'][0] or not x['delegates'][0].strip() else 'delegate_ok'
    s = x['spoken']
    if not s: return 'silent'
    if re.search(r"sorry|don't have|无法|不能|抱歉", s, re.I): return 'refuse'
    if re.search(r"I'll|I will|I'm checking|我来|我会|我这就|正在|Of course|Sure|好的|I can do", s) and not re.search(r'\d', s): return 'announce_no_handoff'
    return 'answer_directly'
for f in sys.argv[1:]:
    d = json.load(open(f)); c = collections.Counter((x.get('type', 'fdb'), cls(x)) for x in d)
    print('==', f.split('/')[-1], len(d))
    for t in sorted({k[0] for k in c}):
        print(' ', t, dict(sorted({k[1]: v for k, v in c.items() if k[0] == t}.items())))
