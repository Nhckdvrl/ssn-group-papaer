"""Known-answer CPU checks for interventions and inference, before held readouts."""
from __future__ import annotations

import itertools
import json

import numpy as np
import torch
from torch import nn
from transformers import OlmoeConfig
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock

import e144145_common as c
from e144145_analyze import crossed_stats, input_stats


def config(experts=4, hidden=8, top_k=2):
    return OlmoeConfig(hidden_size=hidden, intermediate_size=8, num_experts=experts,
                       num_experts_per_tok=top_k, norm_topk_prob=False, hidden_act="silu")


def run():
    torch.set_num_threads(1)
    torch.manual_seed(144)
    cfg = config()
    blocks = [OlmoeSparseMoeBlock(cfg).eval().requires_grad_(False) for _ in range(3)]
    hidden = torch.randn(2, 3, 8)
    mapping = [2, 0, 3, 1]
    checks = {}
    with torch.no_grad():
        for dtype in (torch.float32, torch.bfloat16):
            h = hidden.to(dtype)
            context = torch.autocast("cpu", dtype=torch.bfloat16, enabled=dtype == torch.bfloat16)
            with context:
                original = c.trace(blocks[0], h)
                assembled = c.Assembled(blocks[0], range(4), list(blocks[0].experts))
                identity = c.trace(assembled, h)
                joint = c.Assembled(blocks[0], mapping, c.common_experts(blocks[0], mapping))
                relabeled = c.trace(joint, h)
            assert torch.equal(original["native"], identity["native"])
            assert torch.equal(original["native"], relabeled["native"])
            assert torch.equal(torch.tensor(mapping)[original["selected"]], relabeled["selected"])
            assert torch.equal(original["sum64"], identity["sum64"])
        checks["native_self_and_joint_permutation_FP32_BF16"] = True
        saved = blocks[0].gate.weight.detach().clone()
        blocks[0].gate.weight.zero_()
        native_tied = c.trace(blocks[0], hidden)
        joint_tied = c.trace(c.Assembled(blocks[0], mapping, c.common_experts(blocks[0], mapping)), hidden)
        assert torch.equal(native_tied["native"], joint_tied["native"])
        assert torch.equal(torch.tensor(mapping)[native_tied["selected"]], joint_tied["selected"])
        blocks[0].gate.weight.copy_(saved)
        checks["tied_TopK_preserves_physical_selection_and_sum_order"] = True

        for b in blocks[1:]:
            b.gate.weight.copy_(blocks[0].gate.weight)
        traces = [c.trace(b, hidden) for b in blocks]
        moments, mu = c.cohort(traces)
        generic, mu2 = c.cohort_general(traces)
        for key in moments:
            torch.testing.assert_close(moments[key], generic[key], atol=1e-14, rtol=1e-12)
        torch.testing.assert_close(mu, mu2, atol=0, rtol=0)
        # Check source extraction against the observed native selected products.
        assignment = [0, 2, 1, 2]
        mixed = c.trace(c.Assembled(blocks[0], range(4), [blocks[s].experts[e] for e, s in enumerate(assignment)]), hidden)
        for e, s in enumerate(assignment):
            assert torch.equal(mixed["components"][e]["component"], traces[s]["components"][e]["component"])
        checks["fixed_gate_selected_products_and_population_moments"] = True

        # Heterogeneous support: compare sparse streaming moments with dense truth.
        blocks[1].gate.weight.neg_()
        traces = [c.trace(b, hidden) for b in blocks]
        heterogeneous, _ = c.cohort_general(traces)
        dense = torch.zeros(3, 4, 6, 8, dtype=torch.float64)
        for s, t in enumerate(traces):
            for e, comp in t["components"].items():
                dense[s, e, comp["row"]] = comp["component"].double()
        expected_c = (dense-dense.mean(0)).square().sum(-1).mean(0).sum(0).reshape(2, 3)
        torch.testing.assert_close(heterogeneous["C"], expected_c, atol=1e-14, rtol=1e-12)
        checks["heterogeneous_native_support_moments_match_dense_truth"] = True

    u = np.array([[1., -1.], [-1., 1.], [0., 0.]])
    center = u.mean(0)
    comp_variance = np.square(u-center).mean(0).sum()
    sum_variance = np.square(u.sum(1)-u.sum(1).mean()).mean()
    enumerated = np.mean([np.square(u[s0, 0]+u[s1, 1]) for s0, s1 in itertools.product(range(3), repeat=2)])
    assert abs(enumerated - comp_variance + sum_variance) < 1e-14 and sum_variance == 0
    rng = np.random.default_rng(144)
    maps = rng.integers(0, 3, (8, 2))
    sources = np.concatenate([(maps+s) % 3 for s in range(3)])
    assert np.array_equal(np.stack([(sources == s).sum(0) for s in range(3)]), np.full((3, 2), 8))
    outputs = np.stack([u[m, np.arange(2)] for m in sources])
    np.testing.assert_allclose(outputs.mean(0), center, atol=1e-15)
    checks["complete_source_enumeration_C_minus_V_and_cyclic_first_moment"] = True

    class Constant(nn.Module):
        def __init__(self, value):
            super().__init__()
            self.register_buffer("value", torch.tensor(value, dtype=torch.float32))
        def forward(self, x):
            return self.value.expand(len(x), -1)

    ga, gd = OlmoeSparseMoeBlock(config(2, 2, 1)), OlmoeSparseMoeBlock(config(2, 2, 1))
    ga.gate.weight.data.copy_(torch.tensor([[2., 0.], [0., 0.]]))
    gd.gate.weight.data.copy_(torch.tensor([[0., 0.], [2., 0.]]))
    ba, bd = [Constant([1., 0.]), Constant([0., 1.])], [Constant([2., 0.]), Constant([0., 3.])]
    h = torch.tensor([[[1., 0.]]])
    aa, ad, da, dd = [c.Assembled(g, range(2), b)(h)[0] for g, b in ((ga, ba), (ga, bd), (gd, ba), (gd, bd))]
    interaction = dd-da-ad+aa
    q = float(torch.softmax(torch.tensor([2., 0.]), 0)[0])
    torch.testing.assert_close(interaction, torch.tensor([[[-q, 2*q]]]))
    assert interaction.square().sum() > 0
    checks["nonzero_four_grid_interaction_has_known_answer"] = True

    p = torch.tensor([[[.2, .8], [.7, .3]]], dtype=torch.float64)
    qv = torch.tensor([[[.6, .4], [.1, .9]]], dtype=torch.float64)
    target = torch.tensor([[1, 0]])
    result = c.prediction_metrics(p.log(), qv.log(), target)
    torch.testing.assert_close(result[..., 0], -torch.tensor([[.4, .1]], dtype=torch.float64).log())
    torch.testing.assert_close(result[..., 1], (p * (p.log()-qv.log())).sum(-1))
    torch.testing.assert_close(result[..., 2], (qv * (qv.log()-p.log())).sum(-1))
    assert not torch.allclose(result[..., 1], result[..., 2])
    mask = torch.tensor([[1., 0.]])
    assert float((result[..., 0]*mask).sum()/mask.sum()) == float(-qv[0, 0, 1].log())
    checks["KL_directions_label_alignment_and_mask_reduction"] = True

    rows = [{"source": "x", "file_id": str(i // 2)} for i in range(6)]
    values = np.array([1, 1, 2, 2, 4, 4], dtype=float)
    summary = input_stats(values, rows)
    assert summary["point"] == 7/3 and summary["file_clusters"] == 3
    summary = crossed_stats(np.repeat(values[None, :], 8, 0), rows)
    assert summary["source_mc_se"] == 0 and len(summary["source_base_points"]) == 8
    checks["file_clusters_and_eight_MC_units_not_training_seeds"] = True
    result = {"status": "passed", "CPU_only": True, "checks": checks, "source_sha256": c.code_proof()}
    c.write(c.WB / "results/e144145_self_test.json", result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
