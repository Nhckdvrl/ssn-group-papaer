"""minWM Wan Action2V teacher-forcing config with seam-targeted context corruption (E28).

Identical to the official stage1_ar_tf except the clean-context step: SeamContextNoise (scripts/seam_aug.py)
noises the last SEAM_K latents of every block with probability SEAM_P. SEAM_K=0 gives the official recipe.
"""
import os

_base_ = os.path.join(os.environ["WB"], "vendor/minWM/configs/wan21/action2v/train/stage1_ar_tf.py")

recipe = dict(
    batch_preprocessors=[
        dict(type="LatentToDevice"),
        dict(type="FlowNoise", uniform_across_frames=False, num_frame_per_block=4),
        dict(type="seam_aug:SeamContextNoise", num_frame_per_block=4, k=int(os.environ.get("SEAM_K", "1")),
             p=float(os.environ.get("SEAM_P", "0.5")), t_lo=200, t_hi=900),
    ],
)
