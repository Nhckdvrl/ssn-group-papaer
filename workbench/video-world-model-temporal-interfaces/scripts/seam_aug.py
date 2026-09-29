"""Seam-targeted clean-context corruption for minWM teacher-forcing training (mechanism test, E28).

Hypothesis: at a block seam the causal student copies the motion it observes in the clean context (last cached
latents) instead of reading the control, because that cue is almost always right in training. This preprocessor
replaces CleanContextNoiseAug: with probability `p` per sample, the last `k` latents of every block (the context
that the next block's first latent sees across the seam) are noised to a random timestep in [t_lo, t_hi]; all
other context latents stay clean (aug_t = 0). `k=0` or `p=0` reproduces the official clean context.
"""
import torch

from minwm.processors.base import BatchPreprocessor
from minwm.sampling.schedulers import FlowMatchingScheduler


class SeamContextNoise(BatchPreprocessor):
    def __init__(self, num_frame_per_block: int = 4, k: int = 1, p: float = 0.5, t_lo: int = 200,
                 t_hi: int = 900, scheduler: FlowMatchingScheduler | None = None) -> None:
        self.nb, self.k, self.p, self.t_lo, self.t_hi = num_frame_per_block, k, p, t_lo, t_hi
        self.scheduler = scheduler

    def __call__(self, batch: dict, device: torch.device) -> dict:
        clean, noise = batch["clean_latent"], batch["noise"]
        B, F = clean.shape[:2]
        ts = self.scheduler.timesteps.to(device)
        sel = torch.zeros(B, F, dtype=torch.bool, device=device)
        if self.k > 0 and self.p > 0:
            from minwm.distributed import get_rng_states_tracker
            with get_rng_states_tracker().fork():
                on = torch.rand(B, device=device) < self.p
                cand = ((ts >= self.t_lo) & (ts <= self.t_hi)).nonzero().flatten()
                pick = cand[torch.randint(len(cand), (B, F), device=device)]
            for j in range(self.nb - self.k, F - self.nb, self.nb):  # never the last block (no seam after it)
                sel[:, j:j + self.k] = True
            sel &= on[:, None]
            aug_t = torch.where(sel, ts[pick], torch.zeros_like(ts[pick]))
        else:
            aug_t = torch.zeros(B, F, device=device, dtype=ts.dtype)
        noisy = self.scheduler.add_noise(clean.flatten(0, 1), noise.flatten(0, 1),
                                         aug_t.flatten(0, 1)).unflatten(0, (B, F))
        batch["clean"] = torch.where(sel[..., None, None, None], noisy, clean)
        batch["aug_t"] = aug_t
        return batch
