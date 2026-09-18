"""
S03 / E02 — parameter-locus arms for the causal acquisition test.

The model is split into internal computation h_theta and the native stop
readout w_stop (the lm_head row(s) of the token that terminates an assistant
turn).  Four arms differ ONLY in which of those is allowed to change; the
corpus, format, ordering, and optimizer schedule are shared.

  base   nothing trains
  R      ONLY the stop readout may change.  Implemented as an additive delta on
         the stop row, so every non-stop logit stays bit-exact equal to base.
  Rmlp   steelman of R: the stop logit may be an arbitrary 2-layer function of
         the frozen final hidden state.  Separates "the information is not in
         the state" from "a linear stop readout is not expressive enough".
  S      everything EXCEPT the stop readout may change.  The pretrained stop
         row is restored bit-exactly after every optimizer step.  Note this
         still lets the NON-stop output rows move, so S is "beyond the stop
         readout", not "internal state only".
  Sbody  the strict state-only arm: the ENTIRE output head is frozen, so only
         the transformer body and input embeddings may change.  This is the
         arm that isolates internal computation from any readout change.
  F      everything may change (adaptation ceiling / positive control).
"""
import torch
import torch.nn as nn


class StopReadout(nn.Module):
    """Additive learnable stop-logit head over the frozen final hidden state."""

    def __init__(self, hidden_size, stop_ids, mode="linear", width=512, dtype=torch.float32):
        super().__init__()
        self.stop_ids = list(stop_ids)
        self.mode = mode
        if mode == "linear":
            # zero-init => at step 0 the model is bit-exactly the base model
            self.w = nn.Parameter(torch.zeros(len(self.stop_ids), hidden_size, dtype=dtype))
            self.b = nn.Parameter(torch.zeros(len(self.stop_ids), dtype=dtype))
        elif mode == "mlp":
            self.net = nn.Sequential(
                nn.Linear(hidden_size, width, dtype=dtype),
                nn.GELU(),
                nn.Linear(width, len(self.stop_ids), dtype=dtype),
            )
            nn.init.zeros_(self.net[-1].weight)
            nn.init.zeros_(self.net[-1].bias)
        else:
            raise ValueError(mode)

    def delta(self, h):
        if self.mode == "linear":
            return h.to(self.w.dtype) @ self.w.T + self.b
        return self.net(h.to(self.net[0].weight.dtype))


class ArmModel(nn.Module):
    """Wraps a causal LM and applies the arm's parameter-freedom constraint."""

    def __init__(self, model, stop_ids, arm):
        super().__init__()
        self.model = model
        self.arm = arm
        self.stop_ids = list(stop_ids)
        self.readout = None

        head = model.get_output_embeddings()
        self._head_weight = head.weight
        self._stop_idx = torch.tensor(self.stop_ids, device=head.weight.device)
        self._head_device = head.weight.device

        if arm in ("R", "Rmlp"):
            for p in model.parameters():
                p.requires_grad_(False)
            self.readout = StopReadout(
                model.config.hidden_size, self.stop_ids,
                mode="linear" if arm == "R" else "mlp",
            )
        elif arm == "Sbody":
            # strict state-only: freeze the whole output head, body is free
            for p in model.parameters():
                p.requires_grad_(True)
            head.weight.requires_grad_(False)
            if head.bias is not None:
                head.bias.requires_grad_(False)
            self.register_buffer("_head_ref", head.weight.data.clone())
            self._head_bias_ref = (head.bias.data.clone()
                                   if head.bias is not None else None)
        elif arm == "S":
            for p in model.parameters():
                p.requires_grad_(True)
            # snapshot the pretrained stop readout so it can be restored exactly
            self.register_buffer("_stop_row_ref",
                                 head.weight.data[self._stop_idx].clone())
            self._head_bias_ref = (head.bias.data[self._stop_idx].clone()
                                   if head.bias is not None else None)
        elif arm == "F":
            for p in model.parameters():
                p.requires_grad_(True)
        elif arm == "base":
            for p in model.parameters():
                p.requires_grad_(False)
        else:
            raise ValueError(arm)

    # -- the S constraint is enforced as an exact restore, not just a grad mask,
    #    so optimizer state / weight decay cannot leak into the frozen row.
    def enforce_freeze(self):
        head = self.model.get_output_embeddings()
        if self.arm == "S":
            with torch.no_grad():
                head.weight.data[self._stop_idx] = self._stop_row_ref.to(head.weight.dtype)
                if self._head_bias_ref is not None:
                    head.bias.data[self._stop_idx] = self._head_bias_ref.to(head.bias.dtype)
        elif self.arm == "Sbody":
            with torch.no_grad():
                head.weight.data.copy_(self._head_ref.to(head.weight.dtype))
                if self._head_bias_ref is not None:
                    head.bias.data.copy_(self._head_bias_ref.to(head.bias.dtype))

    def forward(self, input_ids, attention_mask=None):
        if self.readout is not None:
            # every model parameter is frozen in R / Rmlp, so the base forward
            # needs no graph at all: the only gradient path is h -> readout.
            with torch.no_grad():
                out = self.model(input_ids=input_ids, attention_mask=attention_mask,
                                 output_hidden_states=True)
            logits = out.logits.detach()
            h = out.hidden_states[-1].detach()
            d = self.readout.delta(h.to(next(self.readout.parameters()).device))
            d = d.to(logits.device)
            logits = logits.clone()
            for j, sid in enumerate(self.stop_ids):
                logits[..., sid] = logits[..., sid] + d[..., j].to(logits.dtype)
            return logits
        out = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return out.logits

    def trainable_parameters(self):
        ps = [p for p in self.parameters() if p.requires_grad]
        return ps

    def n_trainable(self):
        return sum(p.numel() for p in self.trainable_parameters())
