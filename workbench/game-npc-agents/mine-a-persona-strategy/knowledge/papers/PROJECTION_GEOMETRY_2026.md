# The Geometry of Projection Heads — 2026

- 主源<https://arxiv.org/abs/2605.17180> / <https://openreview.net/forum?id=y4uR1LFClc>；corpus标ICML2026 Poster，官方OpenReview被challenge阻断，**会场尚未独立确认**。PDF SHAc0cf17a760355efa15b7ec8641a56ca37690f3be9ae61ea46ae27395c8bf5be6。
- 已读intro、§5 Thm5.2 augmentation tangent的退化metric与5.3信息rank、§6 CIFAR/ResNet/ViT与Swish/ReLU/head-depth；全部证明/附录与作者code未审完。
- **DOCUMENTED：** projection作为可训练metric/几何缓冲，augmentation不变性可压缩下游有用方向，SSL通常训练后丢弃head；平滑非线性曲率与塌缩不稳定性理论属于该文。不能从几页阅读把所有条件省略成普遍保证。
- **RECONSTRUCTED：** contrastive需求可能扭曲通用embedding→投影吸收几何约束→下游丢head保留更多信息。projection几何、invariance-information tradeoff早有owner。
- **对我们/未排除：** PCSP actor/critic部署时实际使用同φ，无法直接discard；这只是适用条件不同，尚非新贡献。E25需真正路由控制与原生utility证据，不把普通detach或SSL几何重新命名。
