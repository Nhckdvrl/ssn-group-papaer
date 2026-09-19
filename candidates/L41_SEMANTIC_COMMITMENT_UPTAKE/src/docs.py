"""Micro-document shells for L41 continued training.

Every arm (Mp/Mn/Fp/Fn/Ap/An) uses the SAME shell set with the SAME document
ids, so shell frequency, length and framing are matched by construction.
The shell never states or implies whether the embedded event occurred.
"""
import random, hashlib

SHELLS = [
    ("Site log, entry {eid}.\n", "\nEnd of entry.\n"),
    ("Operations record {eid}. Shift: night.\n", "\nFiled by the duty officer.\n"),
    ("Summary of report {eid}.\n", "\nNo further comment was added.\n"),
    ("From the incident register ({eid}):\n", "\nThe register was countersigned the next morning.\n"),
    ("Weekly digest, item {eid}.\n", "\nThe item was then archived.\n"),
    ("Transcript excerpt {eid}.\nSupervisor: Read back the last line.\nClerk: ",
     "\nSupervisor: Understood.\n"),
    ("Station bulletin {eid}. The following entry was posted on the board.\n",
     "\nThe bulletin was taken down a week later.\n"),
    ("Maintenance notebook, page {eid}.\n", "\nThe page was initialled.\n"),
    ("Note {eid} in the facility ledger reads as follows.\n",
     "\nThe ledger is kept in the front office.\n"),
    ("Debrief memo {eid}.\n", "\nCopies were sent to the records office.\n"),
    ("Archive card {eid}.\n", "\nCross-reference: none.\n"),
    ("Daily roster notes, {eid}.\n", "\nRoster notes are retained for one year.\n"),
]

def docs_for(prop, cell, n_docs, seed=0):
    """n_docs micro-documents for one proposition in one condition."""
    rng = random.Random(f"{prop['pid']}|{seed}")
    order = list(range(len(SHELLS)))
    rng.shuffle(order)
    sent = prop["sent"][cell]
    out = []
    for k in range(n_docs):
        pre, post = SHELLS[order[k % len(SHELLS)]]
        eid = 1000 + int(hashlib.sha1(f"{prop['pid']}|{k}".encode()).hexdigest()[:8], 16) % 9000
        out.append(pre.format(eid=eid) + sent + post)
    return out
