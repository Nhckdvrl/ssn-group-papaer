"""Run the official GenEval scorer (djghosh13/geneval@af4902f, evaluation/evaluate_images.py) under
mmdet 3.3, by converting mmdet-3 DetDataSample outputs into the mmdet-2 per-class (bbox, segm) lists
that the official script expects. Scoring logic (thresholds, NMS, CLIP colour classifier, position
rule) is the official code, unchanged.

Usage (mg-eval env): python geneval_mmdet3.py <imagedir> <outfile>
"""
import os
import runpy
import sys

import numpy as np

MG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
G = os.path.join(MG, "vendor", "geneval")
CFG = os.path.join(G, "mmdetection", "configs", "mask2former", "mask2former_swin-s-p4-w7-224_8xb2-lsj-50e_coco.py")

import mmdet.apis as apis  # noqa: E402

_orig = apis.inference_detector


def inference_detector_v2(model, img):
    ds = _orig(model, img)
    inst = ds.pred_instances
    labels = inst.labels.cpu().numpy()
    scores = inst.scores.cpu().numpy()
    boxes = inst.bboxes.cpu().numpy()
    masks = inst.masks.cpu().numpy() if "masks" in inst else None
    n_cls = len(model.dataset_meta["classes"])
    bbox, segm = [], []
    for c in range(n_cls):
        k = labels == c
        bbox.append(np.concatenate([boxes[k], scores[k, None]], 1).astype(np.float32).reshape(-1, 5))
        segm.append([m for m in masks[k]] if masks is not None else [])
    return (bbox, segm)


apis.inference_detector = inference_detector_v2

if __name__ == "__main__":
    imagedir, outfile = sys.argv[1], sys.argv[2]
    sys.argv = ["evaluate_images.py", imagedir, "--outfile", outfile,
                "--model-path", os.path.join(G, "models"), "--model-config", CFG]
    sys.path.insert(0, os.path.join(G, "evaluation"))
    runpy.run_path(os.path.join(G, "evaluation", "evaluate_images.py"), run_name="__main__")
