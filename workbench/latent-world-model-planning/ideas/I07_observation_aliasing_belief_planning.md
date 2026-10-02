# I07 — Observable goal ≠ control state: belief-aware visual planning

- **状态：** SEED / broad problem mine
- **母问题：** image-goal latent planner 在 observation aliasing 下，goal-comparable visual state 与 control-sufficient hidden dynamic state 是否需要不同的表示/规划语义？
- **不是：** “多给几帧更好”、hidden-state probe、generic POMDP。
- **直接近邻：** FIRM-WM（typed config/dynamic fiber + interventions）、UWM-JEPA（belief-space predictor）、Flow Equivariant WM（ICML'26 structured memory）、I-TAP（POMDP/regime-shift planning）、UAI'26 selection theorem（belief-like memory necessity）。
- **Exact delta 候选：** compact reward-free **image-goal MPC** 中，same/near-identical observation + different hidden state 是否系统改变 candidate action ordering；deterministic history state何时足够，何时必须保留 multi-hypothesis uncertainty；这种区别能否预测闭环规划失败。
- **最小 proof-of-problem：** 不训练新方法，构造/筛选 simulator states：rendered observation相同或受控近似，但 velocity/contact/friction/regime不同；计算/rollout candidate actions的真实 utility，验证 action argmin/argmax发生改变。
- **升级条件：** baseline latent planner在这种 natural aliasing下产生显著 decision regret；简单 frame stacking/history不是完整解释；至少第二类 hidden factor复现。
- **方法只有在证据后出现：** typed belief state、stochastic/multi-hypothesis rollout、risk/information-aware scoring等都只是候选，不预注册为答案。
- **最大 collision：** FIRM-WM 已占 goal/dynamic factorization；UWM-JEPA 已占 belief-space prediction。我们的 novelty 若成立必须是 **belief/aliasing → action choice → image-goal planning consequence + regime distinction**，而不是再命名 state factorization。
- **对应：** E11 → conditional E12。
