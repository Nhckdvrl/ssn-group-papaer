# Language Models Struggle to Use Representations Learned In-Context（ACL2026正式主文）

证据：[正式论文](https://aclanthology.org/2026.acl-long.676/)主文§1–7完整、AppA–C文字与设置、D的task/baseline开头读；E–J未深读。Brown/NYU/Google Research/DeepMind。17页61535字符PDF外置，SHA15a346dbb6b5d00d55e1a0ce0913ec53d8f436ab9fb74f313a289f005fcfc4d2。

1. **形态：** 构念区分＋新下游测量＋可行替代表示，未给修复算法。
2. **压力：** Park发现随机游走使token几何学到latent topology；但适应性agent需要把新结构用于另一行为，仅可解码不够。
3. **改变前提：** 有结构几何不自动是可灵活部署world model。表示对象必须同时问它在哪个后续context实际可用。
4. **idea来源（DOCUMENTED/RECONSTRUCTED）：** Park2025 representation learning的强阳性→Hu/Frank延迟next-word失败→把这二者交叉，source几何好而后续预测差；再加入必须学新规则的AWM，让“world model”承担可操作的下游后果。作者明确借用Hu/Frank，具体思路演化为重建。
5. **近邻距离：** Park只有形成结构，此文增加部署；Hu/Frank自然语言延迟，此文synthetic可量化结构；Vafa世界模型泛化，此文部署时新语义；Lubana工具显示几何，此文直接下游；CoT计算理论提供替代路径，此文只行为测试，不证明CoT内部算法。一般“编码了却用不好”已有明确ownership。
6. **方法/数据/基线：** 16/25节点line与4×4/5×5grid，随机单token词绑定；sliding50测normalized Dirichlet energy/Manhattan–activation distance correlation。Gemma3-4/12/27B-it、OLMo2-13B。按末层与倒数第三层DC选择context，next-token/AWM每条件1000词分配；assistant-prefill与user-instruction。AWM 1/2/3步rule、通常10例（4×4两步6例）。显式坐标source作替代；一跳attested adjacency猜测约line50%/grid30%，不把这称学规则。闭源Gemini2.5与GPT5系列只读作者结果，我们不调用这些API。
7. **结果/短板：** instruction预测明显低于prefill，两个source几何比约1；AWM开放模型大多弱，4×4部分约40%，explicit grid部分>75%。frontier line较好/grid下降，explicit grid Gemini接近ceiling；直接说出grid尺寸的宽松判分并不检查词→位置映射。几何在rule例子退化支持部署缺口，但论文没有因果切断/恢复已学表示来证明其“inert”机制；prompt条件同时改role/位置/interval。CoT消融Flash有时升、Pro降，不能简单归结思考普遍解决。公开评审分数未核对。
8. **可迁移动作：** 把宽泛world-model赞誉变成必须调用新结构的操作；用显式结构展示问题不是规则本身不可做；明确判断成功需要的对象比宽松描述评分更严格。
9. **对我们：** E63–68的一般cross-use gap若仅换GP数据，增量不足。真正可追的是修订过程的特定因果功能：正确局部说明如何保持或扰乱下一绑定、什么时候修复局部却改变全局的方向。该假说仍待证，不能据近邻关线；若E71是null，就据实际关系脚印改问题，而非补防御控制。
