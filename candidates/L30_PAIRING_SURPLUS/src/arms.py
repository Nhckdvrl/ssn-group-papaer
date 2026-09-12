"""Shared construction of the L30 E01 training arms.

The scientific estimand is the marginal causal value of the joint X<->Y
correspondence at fixed prompt marginal P_X and response marginal P_Y:

    Pairing Surplus = Performance(P_XY) - Performance(P_X (x) P_Y)

Four arms, all sharing one pool of (x_i, y_i) and one response multiset:

  P       x_i -> y_i                        correct correspondence
  S       x_{pi(i)} -> y_i  (derangement)   same marginals, WRONG correspondence
  D_mask  x_i -> y_i, but response tokens cannot attend to the instruction
                                            budget/position matched, NO correspondence
  D_rt    (no user turn) -> y_i             An et al. Response Tuning, construct anchor

P and S are matched token-for-token: identical prompt multiset, identical
response multiset, identical per-example loss-token count, identical step count.
P vs S is therefore the artifact-free primary contrast.
"""

SEG_USER_OPEN = "<|user|>\n"
SEG_ASST_OPEN = "\n<|assistant|>\n"

ARMS = ("P", "S", "D_mask", "D_rt")


def eval_prompt(x_text):
    """Inference-time context, identical for every arm (RT paper, section 3)."""
    return SEG_USER_OPEN + x_text + SEG_ASST_OPEN


def build_example(x_ids, y_ids, arm, bos_id, eos_id, user_open_ids, asst_open_ids):
    """Return (input_ids, loss_mask, block_from).

    loss_mask is 1 on response tokens (including the final EOS) and 0 elsewhere,
    mirroring the IT/RT objective of An et al.: in BOTH conditions the loss is
    computed exclusively on response tokens.

    block_from is None except for D_mask, where it is the first index of the
    assistant-open segment. Every query position >= block_from is forbidden to
    attend to positions [1, block_from) -- i.e. the user-open segment and the
    instruction -- while keeping BOS and causal self-attention. The resulting
    information set for the response is exactly {BOS} + assistant-open + response,
    which is the D_rt token content placed at the P positions.
    """
    if arm == "D_rt":
        ids = [bos_id] + list(asst_open_ids) + list(y_ids) + [eos_id]
        n_pre = 1 + len(asst_open_ids)
        loss = [0] * n_pre + [1] * (len(y_ids) + 1)
        return ids, loss, None

    if arm == "D_mask":
        prompt_ids = x_ids
    elif arm == "P":
        prompt_ids = x_ids
    elif arm == "S":
        prompt_ids = x_ids  # caller passes the permuted instruction
    else:
        raise ValueError(arm)

    ids = (
        [bos_id]
        + list(user_open_ids)
        + list(prompt_ids)
        + list(asst_open_ids)
        + list(y_ids)
        + [eos_id]
    )
    block_from = 1 + len(user_open_ids) + len(prompt_ids)
    n_pre = block_from + len(asst_open_ids)
    loss = [0] * n_pre + [1] * (len(y_ids) + 1)
    return ids, loss, (block_from if arm == "D_mask" else None)


def derangement(n, seed):
    """Fixed random permutation with no fixed point (Sattolo's algorithm).

    A fixed point would leave a correctly paired example inside the S arm; with
    n ~ 5e4 a plain shuffle leaves ~1 in expectation. Sattolo's algorithm draws
    uniformly from the n-cycles, which are all fixed-point free.
    """
    import random

    rng = random.Random(seed)
    perm = list(range(n))
    for i in range(n - 1, 0, -1):
        j = rng.randrange(i)  # strictly less than i -> no fixed point
        perm[i], perm[j] = perm[j], perm[i]
    assert all(perm[i] != i for i in range(n))
    return perm
