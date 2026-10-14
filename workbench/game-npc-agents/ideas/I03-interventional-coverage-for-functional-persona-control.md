# I03：从角色可辨认到可组合的利益控制

- **状态：** SEED，来自完整观察的研究idea，尚无方法结论。
- **来源：** P10；E34三seed完整300轮、E37/39原生利益方向与E40真实需求反馈。Full的正面形成与总体utility成本同时保留，不以寻找gap为起点。
- **研究动作：** 区分个体身份、任务中可替代的风格与真正改变利益取舍的属性；干预训练覆盖，研究何种角色经验形成可组合控制。
- **核心问题：** 训练中有很多角色身份，是否等于学会在新背景中单独修改一种利益倾向？角色需要在什么状态保持行为、在什么状态改变策略？
- **本地依据：** 400训练角色只有20种BF配置；五held非C背景完全独立；同样C改动的实际利益机会跨背景差异大。300轮Full在同角度C功能对齐上比No更强，但source整体return三seed更低。不是“persona必然失效”。
- **最小研究动作：** E41先比较普通等义surface augmentation与C配置干预，复用原PPO，不预定新损失。C在每个原16NPC episode中重排，边际完全保持，其他traits／身体／preferred_actions不改，文字随C同步；同原始采样背景与计算预算。NoInfoNCE为首比较，避免扩大identity候选数量成为替代解释。
- **如果得到支持：** 更明确地说明人物干预覆盖怎样影响原生偏好控制，以及何时需功能绑定机制；再考虑用native utility、现有value-aware diversity或因果表征工具提高控制，而不靠增加角色数或读出分数。
- **近邻与定位：** PCSP已有persona conditioning／semantic geometry／ID-OOD权衡，PERSONA和Persona Vectors in Games已有向量组合／策略steering；GCB有功能等价，BC-PMI有局部style证据，DAIL有语言轨迹对齐；SIPO／DOMiNO有近最优多样策略，PPol有保持任务目标的人格变化。增量围绕可区分的角色属性利益变化与可替代风格的训练形成／原生验证，继续精读定位，不因部分重叠自动关闭。
- **可能的普通解释：** 若标准surface／intervention augmentation已经解决，就承认普通数据覆盖的作用；不强行发明新的loss、SFT或GRPO。研究继续围绕可预测条件与跨场景证据推进，无自设科学淘汰bar。
