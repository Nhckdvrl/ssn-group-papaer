"""
S03 / E02 Gate C — prove the parameter freezes are real, not nominal.

Checks, on the real checkpoint and after real optimizer steps:

  1. untied embeddings at the STORAGE level (data_ptr), not the config string;
  2. arm R / Rmlp: every NON-STOP logit is bit-exact identical to the base
     model's, and every model parameter is byte-identical, after training;
  3. arm S: the pretrained stop row is byte-identical after training, while
     other parameters have moved;
  4. arm R at step 0 is bit-exactly the base model (zero-init readout).

If any of these fail, the readout-vs-state inference is not supported and the
implementation must be fixed before interpreting any result.
"""
import sys

import torch, torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
from e01_run import STAGE_REPOS, TURN_END_TOKEN
from e02_arms import ArmModel

# The Layer C model is a CLI argument, not a constant: Layer C moved from
# OLMo-2 1B to the Olmo-3 7B base, and a hard-coded repo here would verify the
# freezes on a model the experiment no longer uses.
FAMILY = sys.argv[1] if len(sys.argv) > 1 else "olmo3-7b"
REPO = STAGE_REPOS[FAMILY]["base"]
OK, BAD = "PASS", "**FAIL**"


# The R/Rmlp claim ("every non-stop logit is bit-exact") is checked in float32.
# The S/Sbody claim is that the FROZEN tensors stay byte-identical, which is a
# dtype-independent property, so those arms are checked in bfloat16 with SGD:
# a 7B fp32 model plus grads plus Adam state is ~116GB and does not fit.
DT = {"R": torch.float32, "Rmlp": torch.float32,
      "S": torch.bfloat16, "Sbody": torch.bfloat16}


def load(dtype=torch.float32, device="cuda"):
    tok = AutoTokenizer.from_pretrained(REPO)
    m = AutoModelForCausalLM.from_pretrained(REPO, dtype=dtype).to(device)
    return tok, m


def main():
    only = sys.argv[2] if len(sys.argv) > 2 else None
    dt = DT.get(only, torch.float32)
    tok, model = load(dt)
    # verify the freezes on the token the ARMS actually train: for a
    # distinct-EOT family that is the turn-end token, not the tokenizer eos
    sids = [tok.convert_tokens_to_ids(TURN_END_TOKEN[FAMILY])]
    print(f"stop ids: {sids} -> {[tok.convert_ids_to_tokens(i) for i in sids]}")

    emb = model.get_input_embeddings().weight
    head = model.get_output_embeddings().weight
    tied = emb.data_ptr() == head.data_ptr()
    print(f"[1] untied at storage level                : "
          f"{OK if not tied else BAD}  (data_ptr equal={tied}, "
          f"config tie={model.config.tie_word_embeddings})")

    ids = torch.tensor([tok.encode("Mercury\nVenus\nEarth\n",
                                   add_special_tokens=False)]).cuda()
    with torch.no_grad():
        ref_logits = model(ids).logits.clone()
    ref_params = {n: p.detach().cpu().clone() for n, p in model.named_parameters()}
    ref_logits = ref_logits.cpu()
    del model
    torch.cuda.empty_cache()

    for armname in (["R", "Rmlp", "S", "Sbody"] if only is None else [only]):
        tok2, m2 = load(DT[armname])
        arm = ArmModel(m2, sids, armname).cuda()
        if arm.readout is not None:
            arm.readout = arm.readout.cuda().float()

        if armname in ("R", "Rmlp"):
            with torch.no_grad():
                l0 = arm(ids)
            same0 = torch.equal(l0.cpu(), ref_logits)
            print(f"[4] {armname}: step-0 output == base (zero init)   : "
                  f"{OK if same0 else BAD}")

        # SGD for the 7B arms: Adam state would double the footprint and the
        # freeze claim does not depend on the optimizer.
        opt = (torch.optim.AdamW(arm.trainable_parameters(), lr=1e-3)
               if armname in ("R", "Rmlp")
               else torch.optim.SGD(arm.trainable_parameters(), lr=1e-2))
        for _ in range(5):
            opt.zero_grad()
            logits = arm(ids)
            # push hard toward the stop token everywhere
            tgt = torch.full(ids.shape, sids[0], device=ids.device)
            F.cross_entropy(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1)).backward()
            opt.step()
            arm.enforce_freeze()

        if armname in ("R", "Rmlp"):
            with torch.no_grad():
                l1 = arm(ids)
            mask = torch.ones(l1.size(-1), dtype=torch.bool, device=l1.device)
            mask[torch.tensor(sids, device=l1.device)] = False
            l1c, mc = l1.cpu(), mask.cpu()
            nonstop_exact = torch.equal(l1c[..., mc], ref_logits[..., mc])
            stop_moved = not torch.equal(l1c[..., ~mc], ref_logits[..., ~mc])
            params_exact = all(torch.equal(p.detach().cpu(), ref_params[n])
                               for n, p in arm.model.named_parameters())
            print(f"[2] {armname}: non-stop logits bit-exact after train: "
                  f"{OK if nonstop_exact else BAD}")
            print(f"    {armname}: stop logit actually moved            : "
                  f"{OK if stop_moved else BAD}")
            print(f"    {armname}: all model params byte-identical      : "
                  f"{OK if params_exact else BAD}")
        else:
            h2 = arm.model.get_output_embeddings().weight
            si = torch.tensor(sids)
            hw = h2.data.cpu()
            stop_frozen = torch.equal(hw[si], ref_params["lm_head.weight"][si])
            other_moved = not torch.equal(hw[0:100],
                                          ref_params["lm_head.weight"][0:100])
            body_moved = not torch.equal(
                dict(arm.model.named_parameters())["model.layers.0.mlp.down_proj.weight"].detach().cpu(),
                ref_params["model.layers.0.mlp.down_proj.weight"])
            print(f"[3] {armname}: pretrained stop row byte-identical : "
                  f"{OK if stop_frozen else BAD}")
            if armname == "Sbody":
                # strict state-only: the WHOLE head must be untouched
                whole_frozen = torch.equal(hw, ref_params["lm_head.weight"])
                print(f"    {armname}: ENTIRE lm_head byte-identical      : "
                      f"{OK if whole_frozen else BAD}")
            else:
                print(f"    {armname}: other lm_head rows did move        : "
                      f"{OK if other_moved else BAD}")
            print(f"    {armname}: transformer body did move          : "
                  f"{OK if body_moved else BAD}")
        del arm, m2
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
