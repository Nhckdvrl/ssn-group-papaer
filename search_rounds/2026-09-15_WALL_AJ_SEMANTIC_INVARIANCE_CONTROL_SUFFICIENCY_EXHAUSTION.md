# WALL-AJ — Semantic invariance vs control-sufficient spatial representation

Date: 2026-09-15
Status: EXHAUSTED / LONGSTANDING ROBOTICS PROGRAM

## Mother question
Large-scale vision/vision-language pretraining encourages semantic invariance: the same object should remain similar across viewpoint, position, and background changes. Robot control, however, requires high sensitivity/equivariance to pose, geometry, contact, and spatial relations. Can a representation become better semantically while discarding information required for action?

## Direct-owner lineage
This tension is already explicit in robot representation learning.

- CLIPort (CoRL 2021/2022) frames the problem almost exactly as semantic 'what' versus spatial 'where': internet-pretrained CLIP representations provide broad semantic understanding but lack the spatial precision needed for fine-grained manipulation. Its two-stream architecture explicitly combines semantic and spatial pathways.
- R3M and subsequent robot representation work study representations pretrained on human video specifically because generic visual representations are not automatically control-sufficient.
- SpatialVLA (2025), RoboGround (CVPR 2025), PointACT (RSS 2026), and related VLA work explicitly injects 3D/spatial/grounding representations on top of pretrained semantic backbones for manipulation.
- Equivariant robot-learning work independently treats the correct object as equivariance—not generic invariance—to task-relevant SE(3) transformations.

## Verdict
The semantic-generalization versus spatial/action-sufficiency distinction is already an organizing principle of modern robotic representation learning, not an unowned theoretical conflict.

## Anti-resurrection
No:
- CLIP/VLM semantic features vs spatial probes;
- semantic-vs-spatial encoder ablations;
- adding depth/3D/keypoints to VLA as a scientific question;
- generic claim that invariance hurts manipulation;
- 'what vs where' rediscovery with a newer VLM.
