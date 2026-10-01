"""Check batched conditional likelihood against direct next-token cross entropy."""
import argparse
import json
from pathlib import Path

import torch

from frozen_probe import Scorer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--legacy-pickle", action="store_true")
    parser.add_argument("--weight-dtype", choices=["bf16", "fp32"], default="bf16")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    if args.legacy_pickle and not manifest["repo"].startswith("nusnlp/JGP-"):
        raise ValueError("Legacy pickle loading restricted to official JGP")
    scorer = Scorer(manifest["path"], 4, args.legacy_pickle, "fp32" if args.weight_dtype == "fp32" else "bf16", args.weight_dtype)
    requests = [("The glass fell because", " someone pushed it."),
                ("The child smiled. ", "Her friend returned."),
                ("", "The window was open."),
                ("雨停了所以", "孩子出去玩了。")]
    checks = []
    for precision in (["fp32"] if args.weight_dtype == "fp32" else ["bf16", "fp32"]):
        if precision == "fp32":
            scorer.model = scorer.model.float()
        scorer.batch = 4
        batched = scorer.score(requests)
        scorer.batch = 1
        single = scorer.score(requests)
        for request, actual, alone in zip(requests, batched, single):
            ids, boundary = scorer.encode(*request)
            inputs = torch.tensor([ids], device="cuda")
            with torch.inference_mode():
                logits = scorer.model(input_ids=inputs, use_cache=False).logits.float()
            losses = torch.nn.functional.cross_entropy(
                logits[0, :-1], inputs[0, 1:], reduction="none")
            reference = -losses[boundary - 1:].sum().item()
            assert actual["tokens"] == len(ids) - boundary
            assert len(actual["token_ll"]) == actual["tokens"]
            assert abs(sum(actual["token_ll"]) - actual["ll"]) < 1e-4
            error = abs(reference - actual["ll"])
            batch_error = abs(alone["ll"] - actual["ll"])
            single_error = abs(reference - alone["ll"])
            # Validate indexing in FP32, and retain BF16 kernel-shape sensitivity.
            if precision == "fp32":
                assert error < 1e-4 * actual["tokens"], (request, error)
                assert batch_error < 1e-4 * actual["tokens"], (request, batch_error)
            checks.append({"precision": precision, "request": request, "tokens": actual["tokens"],
                           "single_reference_error": single_error,
                           "reference_error": error, "batch_error": batch_error})
    result = {"model": manifest, "weight_dtype": args.weight_dtype, "checks": checks, "passed": True,
              "scope": "Four boundary/padding cases, not a full harness reproduction; FP32 tolerance 1e-4 nats/token. BF16 deviations recorded, not asserted equivalent."}
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
