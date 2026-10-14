# E39：跨角色语义方向迁移，拆表征与控制响应（2026-10-14）

- **状态：** PLANNED
- **类型：** EXPLORE，既有I02形成机制的局部因果干预；不新增训练。
- **对应：** I02／P06，E37实际异质性；不是先规定新损失。
- **问题：** 同样的C编辑在人物背景之间产生不同原生利益方向，这更随“从哪一人物提取的语义方向”改变，还是随“当前人物／状态／控制头”改变？
- **竞争解释：** H1，文本编码／共享projection形成依赖背景的属性方向，缺少可组合的功能绑定；H2，控制器与原生利益结构决定响应，单一全局trait方向不该处处相同；H3，整体gain与训练阶段解释，C并无方向特异性。三者可并存，不强迫二选一。
- **设置：** 复用E37全部100held人物／120编辑、原fresh-AEC固定状态、原即时source reward vectors、No／Full三seed的30／100／300检查点。每donor用z_target−z_original除以作者C数值变化方向，得到统一“C增大”chord；在recipient anchor上投影到切空间，再按recipient实际编辑正负及E37共同角度干预。全部donor×recipient方向交换只做廉价frozen actor前向，不生成新游戏规则／数据／回报。半角与全角均保留。
- **额外解释对照：** 同donor=recipient的结果须恢复E37本人的方向与probabilities；随机16方向沿用E37。用每recipient在其12原始状态的平均原生reward-contrast gradient作为局部功能可控性参考，仍匹配相同角度。该gradient读取作者白盒reward，明确不是可部署的人格方法或独立能力证据。
- **读数：** 全部donor／recipient矩阵的动作JS、两policy×两目标完整四格即时expected reward与DD；按原型／职业／训练seed报告，不先选有利人物。识别donor方向特异性、recipient作用和两者交互；所有状态保留，原生利益相容的状态也不删去。
- **阳性对照：** 源actor logits与直接φ注入一致；own-direction恢复E37；球面范数与有限步；原reward重建已在E37对60000动作逐episode完全一致。实现差才修代码，不能作为科学淘汰。
- **噪声地板 + MIE：** 数值复现误差、16随机方向与三训练seed都呈现，不设MIE、百分比通过率或科学bar。
- **混杂审计：** latent方向迁移未必有文本对应，不能称自然指令能力。C修改保留身体／preferred_actions，只改变作者角色style／social reward；即时方向不替代长期utility。mid双编辑非独立人物；角色年龄与其他四特质共同变化，矩阵先描述异质性再用具体反事实区分。persona向量组合／策略steering已有PERSONA、Persona Vectors in Games；GCB／BC-PMI／DAIL已有功能／局部风格／语言轨迹表示原则，本实验借其工具理解原生形成机制，不拿“做过一点”当否定。
- **决策表（跑之前写）：** 依据完整矩阵解释H1/H2/H3及混合情形；若ordinary向量方向已解释，则记录其解释力。若局部功能方向可用而语言方向错位，下一步针对可预测错位研究绑定，不先决定训练。无预设科学淘汰条件。
- **算力预算：** CPU少量分钟，冻结政策，无新RL／付费API；所有GPU继续只按真实任务需要使用，白天总≤8。raw既有cache/runs/e39_*。

## 结果
尚未计算。

首批结果：30轮16.66秒、100轮17.85秒，三seed／两route／所有120×120方向完整保留。own-direction probabilities恢复E37，数值误差见JSON。100轮Full原C方向DD−.00132／−.000097／+.00137，平均跨人物方向−.00100／+.00087／+.00141；相同角度的白盒功能gradient参考+.01688／+.01066／+.01509。这排除了简单“latent完全不能影响该利益”的解释，但未证明自然文本应实现该参考。donor与recipient均有作用及交互；没有一个跨角色统一修复方向被建立。完整300轮与独立战略任务继续，不能按单seed／短期大小判成败。
