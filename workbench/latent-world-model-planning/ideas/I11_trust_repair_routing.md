# I11 — When to trust, repair, or bypass imagination?

- **Program:** R5
- **Status:** SEED
- **Mother question:** 同一个 world model 在不同 state/action/horizon/shift 下可靠性不同；检测到 failure pressure 后，planner 应该选择 replan、shorten horizon、feedback correction、adaptation、fallback intuition/policy，还是继续使用 model？
- **不是:** 再发一个 uncertainty metric；也不是 AdaJEPA/Feedback WM/IMWM 的简单拼接。
- **近邻:** PLDM uncertainty、Control Theory of Predictability、MEND、IMWM、AdaJEPA、Feedback WM、AdaReP、Planning Limits。
- **研究动作:** 先构造 intervention oracle：对同一个 planning state，分别执行可用 recovery actions，测真实 utility lift；然后问已有 reliability signals 能否预测 **intervention ranking**。
- **潜在新对象:** failure-type → useful-repair mapping，而不是“uncertainty高/低”。
- **升级条件:** mapping跨至少两个 shift/failure families稳定；简单单阈值无法解释；可导出低开销 adaptive routing。
- **Pilot:** E18。
