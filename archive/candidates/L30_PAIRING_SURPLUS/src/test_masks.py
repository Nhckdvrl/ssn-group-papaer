"""Construct-validity checks for the D_mask arm.

The scientific claim attached to D_mask is: the response is trained at exactly
the P positions, with exactly the P token budget, but with ZERO information
path from the paired instruction.

Designing test 1 took two failed attempts, both recorded here because they are
the kind of artifact this arm exists to rule out:

  attempt 1 -- compare the masked full sequence against a separate forward pass
  on [BOS] + assistant-open + response with `position_ids` set to the original
  absolute positions. This FAILED (max |logit diff| = 31.4), but the cause was
  the reference, not the mask: transformers does not reproduce the full run from
  jumpy `position_ids`, so the reference was simply a different computation.

  attempt 2 -- vary the instruction text and require the D_mask response logits
  not to move. This also FAILED (0.72), again not from leakage: two instructions
  of different token length put the response at different absolute positions, so
  RoPE moves the logits even under a perfect mask.

The surviving test holds token positions exactly fixed by swapping in a
DIFFERENT instruction OF THE SAME TOKEN LENGTH. Then `block_from`, the sequence
length and every response position are identical, and the only thing that
changed is the content behind the mask. Under a correct mask the response
logits must be bit-identical; the same swap under P moves them by ~26 logits.
"""
import collections
import pathlib
import sys
import unittest

import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from arms import build_example, derangement  # noqa: E402
from train import (  # noqa: E402
    as_mask_mapping,
    build_attention_bias,
    load_backbone,
    load_pool,
)

MODEL = "google/gemma-2-2b"


class MaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.tok, cls.special = load_backbone(MODEL, device="cuda")
        cls.model.eval()
        rows, _ = load_pool(ROOT / "results" / "pool")
        by_len = collections.defaultdict(list)
        for r in rows[:4000]:
            by_len[len(r["x_ids"])].append(r)
        cls.group = max(by_len.values(), key=len)
        cls.y_ids = rows[0]["y_ids"][:60]

    def _resp_logits(self, x_ids, arm, mask=True):
        s = self.special
        ids, loss, bf = build_example(
            x_ids, self.y_ids, arm, s["bos_id"], s["eos_id"],
            s["user_open_ids"], s["asst_open_ids"],
        )
        att = None
        if mask and bf is not None:
            att = as_mask_mapping(
                build_attention_bias([ids], [bf], self.model.dtype, "cuda"), self.model
            )
        with torch.no_grad():
            lg = self.model(
                input_ids=torch.tensor([ids], device="cuda"), attention_mask=att
            ).logits[0]
        return lg[-sum(loss):].float()

    def test_1_dmask_blocks_the_instruction_completely(self):
        a, b, c = (g["x_ids"] for g in self.group[:3])
        self.assertEqual(len(a), len(b))
        self.assertEqual(len(a), len(c))
        d_ab = (self._resp_logits(a, "D_mask") - self._resp_logits(b, "D_mask")).abs().max().item()
        d_ac = (self._resp_logits(a, "D_mask") - self._resp_logits(c, "D_mask")).abs().max().item()
        p_ab = (self._resp_logits(a, "P") - self._resp_logits(b, "P")).abs().max().item()
        print(f"\n[test1] equal-length instruction swap, positions held fixed:"
              f"\n        D_mask A-B={d_ab:.3e}  A-C={d_ac:.3e}   P A-B={p_ab:.3e}")
        self.assertEqual(d_ab, 0.0, "D_mask leaked instruction information")
        self.assertEqual(d_ac, 0.0, "D_mask leaked instruction information")
        self.assertGreater(p_ab, 1.0, "P is insensitive to the instruction?")

    def test_2_mask_is_actually_applied(self):
        """Guards against the mask being silently rebuilt/discarded upstream."""
        a = self.group[0]["x_ids"]
        masked = self._resp_logits(a, "D_mask", mask=True)
        unmasked = self._resp_logits(a, "D_mask", mask=False)
        diff = (masked - unmasked).abs().max().item()
        print(f"[test2] masked vs unmasked same sequence = {diff:.3e}")
        self.assertGreater(diff, 1.0, "custom attention bias had no effect")

    def test_3_random_instruction_tokens_change_nothing(self):
        """Strongest form: arbitrary token ids behind the mask, same length."""
        a = self.group[0]["x_ids"]
        g = torch.Generator().manual_seed(0)
        rnd = torch.randint(10, 200000, (len(a),), generator=g).tolist()
        d = (self._resp_logits(a, "D_mask") - self._resp_logits(rnd, "D_mask")).abs().max().item()
        print(f"[test3] random tokens behind the mask = {d:.3e}")
        self.assertEqual(d, 0.0)

    def test_4_sliding_window_guard(self):
        """The shared full/sliding bias is only valid below the window."""
        win = self.model.config.sliding_window
        bias = torch.zeros(1, 1, win + 1, win + 1, dtype=torch.bfloat16, device="cuda")
        with self.assertRaises(AssertionError):
            as_mask_mapping(bias, self.model)

    def test_5_arm_bookkeeping(self):
        s = self.special
        xi = self.tok("Write a haiku about rain.", add_special_tokens=False)["input_ids"]
        xj = self.tok("Summarise the French Revolution.", add_special_tokens=False)["input_ids"]
        yi = self.tok("Rain taps on the roof.", add_special_tokens=False)["input_ids"]
        args = (s["bos_id"], s["eos_id"], s["user_open_ids"], s["asst_open_ids"])

        p_ids, p_loss, p_bf = build_example(xi, yi, "P", *args)
        s_ids, s_loss, _ = build_example(xj, yi, "S", *args)
        d_ids, d_loss, d_bf = build_example(xi, yi, "D_mask", *args)
        r_ids, r_loss, r_bf = build_example(xi, yi, "D_rt", *args)

        for m in (s_loss, d_loss, r_loss):
            self.assertEqual(sum(p_loss), sum(m))
        for ids, loss in ((p_ids, p_loss), (s_ids, s_loss), (d_ids, d_loss), (r_ids, r_loss)):
            self.assertEqual([i for i, k in zip(ids, loss) if k], yi + [s["eos_id"]])
        self.assertEqual(p_ids, d_ids)
        self.assertEqual(len(s_ids) - len(p_ids), len(xj) - len(xi))
        self.assertIsNone(p_bf)
        self.assertIsNone(r_bf)
        self.assertEqual(d_bf, 1 + len(s["user_open_ids"]) + len(xi))

    def test_6_derangement_has_no_fixed_point(self):
        for seed in (0, 1, 1730):
            perm = derangement(5000, seed)
            self.assertEqual(sorted(perm), list(range(5000)))
            self.assertFalse(any(perm[i] == i for i in range(5000)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
