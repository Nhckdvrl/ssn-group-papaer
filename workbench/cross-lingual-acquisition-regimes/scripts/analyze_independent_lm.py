"""Paired within-language loss changes; no cross-language competence ranking."""
import argparse
import json
import math
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("control")
    parser.add_argument("treated")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    control, treated = [json.loads(Path(p).read_text()) for p in [args.control, args.treated]]
    assert control["corpus_sha256"] == treated["corpus_sha256"]
    cr, tr = control["rows"], treated["rows"]
    assert len(cr) == len(tr)
    assert [(r["domain"], r["language"], r["id"], r["text"]) for r in cr] == [(r["domain"], r["language"], r["id"], r["text"]) for r in tr]
    result = {"control": control["model"], "treated": treated["model"],
              "corpus_sha256": control["corpus_sha256"], "cells": {},
              "limits": control["limits"] + " Exploratory item bootstrap, one training seed. Lower loss does not prove reasoning acquisition."}
    rng = np.random.default_rng(20260930)
    for domain, lang in sorted({(r["domain"], r["language"]) for r in cr}):
        indices = [i for i, r in enumerate(cr) if (r["domain"], r["language"]) == (domain, lang)]
        nll = np.array([[-cr[i]["scores"]["ll"], -tr[i]["scores"]["ll"]] for i in indices])
        sizes = {"byte": np.array([len(cr[i]["text"].encode("utf-8")) for i in indices]),
                 "char": np.array([len(cr[i]["text"]) for i in indices])}
        assert all(cr[i]["scores"]["tokens"] == tr[i]["scores"]["tokens"] for i in indices)
        cell = {"n": len(indices)}
        samples = rng.integers(len(indices), size=(10000, len(indices)))
        for unit, lengths in sizes.items():
            bits = nll.sum(axis=0) / lengths.sum() / math.log(2)
            delta = (nll[:, 1] - nll[:, 0]) / math.log(2)
            boot = delta[samples].sum(axis=1) / lengths[samples].sum(axis=1)
            cell[unit] = {"control_bits": bits[0], "treated_bits": bits[1],
                          "delta_bits": bits[1] - bits[0], "paired_95ci": np.quantile(boot, [.025, .975]).tolist()}
        result["cells"][f"{domain}/{lang}"] = cell
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["cells"], indent=2))


if __name__ == "__main__":
    main()
