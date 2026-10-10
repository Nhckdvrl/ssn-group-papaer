# Beyond Owls: Subliminal Learning Can Transfer Learned Capabilities and Backdoors（预印本）[主文§1–7]

[v1正文](https://arxiv.org/html/2610.10657v1)。此卡学习实验逻辑，不另开ICES之外的蒸馏任务；接受状态未核对。

1. **形态：** 扩展现象范围并检验简单替代解释。
2. **压力：** 偏好迁移未区分已有行为被激活与新能力信息被传递。
3. **前提改变：** 新随机函数、已有能力增强、条件触发与环境行动，是不同解释层次。
4. **idea来源：** 以下链条RECONSTRUCTED；不把章节顺序当发现顺序。
5. **距离：** 原subliminal learning、steering-vector distillation与LoRA近似steering工作。
6. **关键实验：** 未知随机MLP排除预训练已有该具体函数；线性基线区分预测层次。ID表现相近的student/vector在小数与文字输入上分化。触发/非触发及未见名字检验条件选择性；普通教师与随机向量教师控制一般训练扰动。
7. **边界：** 只限制被测试的单层固定vector；不同MLP非线性证据不一致；attention/all-linear配置同时改变教师与学生；logits与采样比较也并非处处单变量；没有统一迁移机制。
8. **研究动作：** 寻找正常条件下同预测的解释，在有意义的新条件下怎样分化；对照由证据缺口推出。
9. **对ICES：** E85在原条件预测好，E86量级外推失败应如实记录；不能因相对误差略小就继续称解释成功。异常是否值得追，要看它帮助回答哪个自然计算问题。
