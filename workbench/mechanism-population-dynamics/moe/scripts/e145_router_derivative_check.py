"""Analytical interface check, E145 card: not a training/dynamics experiment."""
from __future__ import annotations

import json

import torch
from transformers import OlmoeConfig
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock

import e144145_common as c


def main():
    torch.set_num_threads(1)
    torch.manual_seed(145)
    z = torch.randn(64, dtype=torch.float64, requires_grad=True)
    f, g = torch.randn(64, 8, dtype=torch.float64), torch.randn(8, dtype=torch.float64)
    indices = z.topk(8).indices
    mask = torch.zeros(64, dtype=torch.bool)
    mask[indices] = True
    p = z.softmax(0)
    y = (p[indices, None]*f[indices]).sum(0)
    observed = torch.autograd.grad(y @ g, z, retain_graph=True)[0]
    expected = p * (mask * (f @ g) - y @ g)
    torch.testing.assert_close(observed, expected, atol=1e-14, rtol=1e-12)
    w = p[indices]/p[indices].sum()
    yn = (w[:, None]*f[indices]).sum(0)
    normalized = torch.autograd.grad(yn @ g, z)[0]
    assert float(observed[~mask].abs().max()) > 1e-6
    assert float(normalized[~mask].abs().max()) < 1e-14
    # Check the actual registered HF interface, including its non-renormalized gate.
    config = OlmoeConfig(hidden_size=8, intermediate_size=8, num_experts=4,
                         num_experts_per_tok=2, norm_topk_prob=False, hidden_act="silu")
    block = OlmoeSparseMoeBlock(config)
    h, loss_direction = torch.randn(1, 1, 8), torch.randn(8)
    output, logits = block(h)
    grad = torch.autograd.grad((output*loss_direction).sum(), block.gate.weight)[0]
    with torch.no_grad():
        p_actual = logits.softmax(-1)[0]
        selected = logits.topk(2, -1).indices[0]
        indicator = torch.zeros(4)
        indicator[selected] = 1
        functions = torch.stack([e(h.reshape(1, 8))[0] for e in block.experts])
        scalar = p_actual * (indicator*(functions @ loss_direction) - output.reshape(-1) @ loss_direction)
        expected_actual = scalar[:, None]*h.reshape(1, 8)
    torch.testing.assert_close(grad, expected_actual, atol=1e-8, rtol=1e-5)
    result = {"status": "passed", "CPU_only": True, "scope": "Algebra/autograd/interface check only, not evidence about training trajectories",
              "synthetic_nonrenormalized_max_formula_error": float((observed-expected).detach().abs().max()),
              "synthetic_unselected_router_gradient_max_abs": float(observed[~mask].detach().abs().max()),
              "synthetic_renormalized_unselected_router_gradient_max_abs": float(normalized[~mask].detach().abs().max()),
              "tiny_HF_nonrenormalized_formula_max_error": float((grad-expected_actual).abs().max()),
              "script_sha256": c.sha(__file__), "actual_HF_module": __import__("transformers").__version__}
    c.write(c.WB / "results/e145/router_derivative_check.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
