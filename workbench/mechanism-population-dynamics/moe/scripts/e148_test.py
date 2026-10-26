"""CPU known-answer checks for native full-model E148 before GPU experiments."""
from __future__ import annotations
import collections
import copy
import hashlib
import json
import tempfile
from pathlib import Path
import numpy as np
import torch
from transformers import OlmoeConfig, OlmoeForCausalLM
import e148_common as c


def main():
    torch.set_num_threads(1); torch.manual_seed(148)
    config = OlmoeConfig(vocab_size=64, hidden_size=16, intermediate_size=16, num_hidden_layers=2,
                         num_attention_heads=2, num_key_value_heads=2, num_experts=4, num_experts_per_tok=2,
                         attention_dropout=0., tie_word_embeddings=False, norm_topk_prob=False, router_aux_loss_coef=.001,
                         max_position_embeddings=32)
    config._attn_implementation = "eager"
    reference = OlmoeForCausalLM(config).bfloat16().eval()
    master = copy.deepcopy(reference).float()
    tokens = torch.randint(0, 64, (2, 9))
    identities = [id(p) for p in master.parameters()]
    original = c.old.tensor_hash(master.state_dict())
    r = reference(input_ids=tokens[:, :-1], use_cache=False, output_router_logits=True)
    ce = torch.nn.functional.cross_entropy(r.logits.float().reshape(-1, 64), tokens[:, 1:].reshape(-1))
    expected_loss = ce+.001*r.aux_loss
    out = c.shader(master, tokens[:, :-1], routers=True)
    assert torch.equal(r.logits, out.logits)
    assert all(p.dtype == torch.float32 for p in master.parameters()) and identities == [id(p) for p in master.parameters()]
    assert c.old.tensor_hash(master.state_dict()) == original
    actual_loss, actual_ce, actual_aux = c.objective(master, tokens)
    torch.testing.assert_close(actual_loss, expected_loss, atol=0, rtol=0)
    actual_loss.backward(); expected_loss.backward()
    max_grad = 0.
    for (name, p), (other, q) in zip(master.named_parameters(), reference.named_parameters()):
        assert name == other
        if p.grad is not None:
            assert p.grad.dtype == torch.float32 and q.grad is not None
            max_grad = max(max_grad, float((p.grad-q.grad.float()).abs().max()))
            torch.testing.assert_close(p.grad, q.grad.float(), atol=1e-6, rtol=1e-4)
    checks = {"BF16_native_vs_functional_shader_exact": True, "functional_restores_FP32_parameter_identity": True,
              "manual_next_token_and_native_aux_match": True, "FP32_master_gradient_max_abs_from_native_BF16": max_grad}
    master.zero_grad(set_to_none=True)
    optimizer = c.make_optimizer(master)
    before = {k: p.detach().clone() for k, p in master.named_parameters()}
    # Tiny model has fewer layers; invoke the objective directly, avoiding real-model probes.
    for step in range(3):
        optimizer.zero_grad(set_to_none=True)
        loss, _, _ = c.objective(master, tokens)
        loss.backward(); torch.nn.utils.clip_grad_norm_(master.parameters(), 1.); optimizer.step()
    changed = sum(int((p-before[k]).abs().sum() > 0) for k, p in master.named_parameters())
    assert changed > 0
    checks["small_updates_retained_in_FP32_masters"] = True
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)/"tiny.pt"
        c.save_torch(path, {"state": c.cpu_tree(master.state_dict()), "optimizer": c.cpu_tree(optimizer.state_dict()), "buffers": c.buffer_state(master)})
        cp = torch.load(path, mmap=True, map_location="cpu", weights_only=False)
        restored = OlmoeForCausalLM(config).float().eval(); restored.load_state_dict(cp["state"])
        c.restore_buffers(restored, cp["buffers"])
        ropt = c.make_optimizer(restored); ropt.load_state_dict(cp["optimizer"])
        for model, opt in ((master, optimizer), (restored, ropt)):
            opt.zero_grad(set_to_none=True)
            loss, _, _ = c.objective(model, tokens)
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.); opt.step()
        for p, q in zip(master.parameters(), restored.parameters()):
            assert torch.equal(p, q)
    checks["saved_optimizer_parent_resumes_exact_update"] = True
    rng = np.random.default_rng(148)
    pool = rng.integers(0, 64, (128, 2, 9), dtype=np.uint16)
    a, b = list(range(128)), rng.permutation(128).tolist()
    counts = lambda order: collections.Counter(c.array_sha(pool[i]) for i in order)
    assert counts(a) == counts(b)
    start = hashlib.sha256(b"suffix").hexdigest()
    def following(order):
        h = start
        for i in order: h = c.chain(h, pool[i])
        return h
    assert following(a) == following(list(a)) and following(a) != following(b)
    checks["pulse_complete_batch_multiset_and_suffix_chain"] = True
    from e144145_analyze import input_stats
    rows = [{"source": "x", "file_id": str(i//2)} for i in range(6)]
    stats = input_stats(np.array([1., 1., 2., 2., 4., 4.]), rows, 148001)
    assert stats["point"] == 7/3 and stats["file_clusters"] == 3
    checks["paired_input_file_units"] = True
    result = {"status": "passed", "CPU_only": True, "checks": checks, "source_sha256": c.code_proof(), "software": c.software()}
    c.write(c.RESULT / "self_test.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
