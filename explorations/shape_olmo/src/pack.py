"""Pack docs into contiguous 8192-token windows (docs joined by EOS), shared by every model.

data/pack_<domain>.npz: ids (S, L) int32; doc, cs, ce (S, L) int32 = source doc index and
character span of each token in that doc's text (-1 for the EOS separator).
"""
import json, sys
import numpy as np
from transformers import AutoTokenizer

L = 8192


def main(tok_path, root, domains):
    tok = AutoTokenizer.from_pretrained(tok_path)
    eos = tok.eos_token_id
    for dom in domains:
        ids, doc, cs, ce = [], [], [], []
        for line in open(f"{root}/data/docs_{dom}.jsonl"):
            d = json.loads(line)
            enc = tok(d["text"], add_special_tokens=False, return_offsets_mapping=True)
            n = len(enc.input_ids)
            ids += enc.input_ids + [eos]
            doc += [d["doc"]] * n + [-1]
            cs += [a for a, b in enc.offset_mapping] + [-1]
            ce += [b for a, b in enc.offset_mapping] + [-1]
        S = len(ids) // L
        arr = lambda x: np.asarray(x[:S * L], dtype=np.int32).reshape(S, L)
        np.savez(f"{root}/data/pack_{dom}.npz", ids=arr(ids), doc=arr(doc), cs=arr(cs), ce=arr(ce))
        print(dom, "tokens", len(ids), "windows", S)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3].split(","))
