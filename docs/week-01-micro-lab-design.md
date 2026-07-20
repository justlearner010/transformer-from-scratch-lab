# Week 1 Micro-Lab 设计契约（提案）

> 状态：待课程验证的目标结构。本文不改变当前 Week 1、学习者答案或 Agent 状态；
> 实现迁移必须在本提案确认后另开开发任务。

## 1. 能力问题与现有证据

能力问题不变：**给定一个无 batch 维的 token 矩阵，学习者能否独立解释、实现并诊断单头 scaled dot-product attention？**

已有证据：Week 0 留下了矩阵、shape、点积与 stable softmax 的学习资产；当前
Week 1 的 Gate 0 已暴露 `K.T` 与 shape 链需要即时反馈。未知的是：学习者能否把
每个 attention 子机制在代码和解释上独立掌握，再将它们可靠组合。

因此不再采用“先集中阅读/推导、最后一次大 Lab”的结构。每个 P0 子机制都在
刚学完时进入一个最小实验；最终 Lab 只验证组件组合和迁移，而不承担发现全部基础
错误的职责。

## 2. 知识地图与强度

| 节点 | 类型 | 当前 → 目标 | 依赖角色 | 优先级与理由 | 任务层 | 最小独立证据 |
| --- | --- | --- | --- | --- | --- | --- |
| shape 与投影契约 | contract + mechanism | unknown → D3 | 硬前置 | P0：所有后续矩阵计算依赖它 | T1 → T3 | 预测 shape、运行 trace、解释 `K.T` |
| score 语义 | mechanism | unknown → D4 | 硬前置 | P0：决定 query 与 key 如何比较 | T1 → T4 | 转置反例与行列语义解释 |
| stable softmax | mechanism + diagnosis | unknown → D4 | 硬前置 | P0：axis/溢出会整体破坏权重 | T1 → T4 | 极端值、错误 axis、性质检查 |
| value 读取 | mechanism | unknown → D3 | 硬前置 | P0：区分“匹配”与“读取内容” | T1 → T4 | 改 V 的预测与验证 |
| Q/K/V 投影 | procedure + contract | unknown → D3 | 核心组件 | P1：为整合提供输入 | T2 → T3 | 输入边界、shape、非原地修改 |
| attention 组装 | integration | unknown → D4 | 整合 | P0：本周唯一端到端能力 | T3 → T5 | 只调用已验证组件的组合实现 |
| 故障诊断与 inspector | diagnosis + integration | unknown → D4 | 下游 | P1：检验可修复、可迁移理解 | T4 → T5 | 一次真实失败与两次预测 |

P0 仍只有四个机制瓶颈与一个整合节点；P1 的投影与 inspector 不因形式对称而各自
增加一个“大作业”。

## 3. 依赖图、范围与非目标

```text
shape trace
  ├→ score probe (Q @ K.T)
  ├→ Q/K/V projection
  └→ stable softmax
score probe + stable softmax
  → value read (weights @ V)
Q/K/V projection + score probe + stable softmax + value read
  → attention composition
  → failure diagnosis + inspector transfer
```

范围：单样本、单头、NumPy 前向计算；每个 micro-lab 只改变一个机制或性质。

非目标：为每个术语强行创建代码任务；batch、多头、mask、训练；让 Agent 自动改
学生代码；用“所有测试通过”代替解释或迁移证据。

## 4. 结构兼容与迁移决定

| 角色 | 当前路径/模式 | 分类 | 目标路径/模式 | 迁移影响 |
| --- | --- | --- | --- | --- |
| 周导航 | `weeks/week-01/README.md` | canonical | 同一路径，改为交替式顺序 | 更新入口链接和完成定义 |
| 理论材料 | `resources/week-01/*.md` | canonical | 同一路径，每段链接到对应 micro-lab | 每段增加“预测后运行”入口 |
| 任务链 | `tasks/week-01.md` | incomplete | 同一路径，Gate 改为机制→实验对 | 删除“Gate 5 才开始 Lab”的表达 |
| 可运行练习 | 单个 `labs/week-01/src/attention.py` | incomplete | `labs/week-01/micro/<nn>-<name>/` 加 `compose/` | 保留 `labs/week-01/` 作为唯一 Lab 根目录 |
| 公开测试 | 单个 `labs/week-01/tests/` | incomplete | 每个 micro-lab 有局部测试；`compose/` 有组合测试 | 公开测试从脚手架检查升级为局部性质检查 |
| 评分入口 | `labs/week-01/run_grade.py` | canonical | 同一路径，按 micro-lab/compose 分类报告 | 不暴露参考实现 |
| 学习证据 | `homework_answer/week-01/gate-XX.md` | canonical | 同一路径，一 Gate 一份“预测/实验/解释/自检” | 由 Agent 生成对应模板 |

`labs/week-01/micro/` 是现有 `labs/week-01/` 下的细分，不创建第二套课程目录。
`compose/` 也不是第二个“大 Lab”，而是同一 Lab 根目录的整合子任务。

## 5. 跨阶段产物契约

每个 micro-lab 必须具备以下固定接口：

```text
labs/week-01/micro/<nn>-<mechanism>/README.md
labs/week-01/micro/<nn>-<mechanism>/starter.py
labs/week-01/micro/<nn>-<mechanism>/tests/test_<mechanism>.py
homework_answer/week-01/gate-<nn>.md
```

| 字段 | 约束 |
| --- | --- |
| README | 只说明一个机制、最小输入、预测问题、运行命令、通过性质、常见失败类别。 |
| starter | 只暴露本机制的公共函数；不提前实现下一机制。 |
| 测试 | 检查一个机制性质与一个边界/变体；不得只断言某份固定输出。 |
| 作答 | 固定为“预测、实验结果、机制解释、提交自检”；只有需要推导时才增加推导栏。 |
| Agent | 仅根据 manifest 的 criterion、测试输出与已 commit 证据判定；不得直接写实现。 |
| 组装 | 只能调用已通过的公共组件；组合 Gate 的测试要检测组件调用与数据流，而非接受重写实现。 |

Week 0 是 pre-Agent 的历史周，保留其一份学习记录作为已命名的兼容性差异；从 Week 1
起，一 Gate 一证据文件是标准。

## 6. 目标任务链

| 顺序 | micro-lab | 学习动作 | 立即反馈 | 解锁证据 |
| --- | --- | --- | --- | --- |
| 0 | `00-shape-trace` | 预测 `XW`、Q/K/V、`Q@K.T`、weights、output 的 shape，再运行最小 trace | shape 不闭合或 `K.T` 解释错误 | 预测与 trace 一致，能说明转置 |
| 1 | `01-score-probe` | 在给定 Q/K 上实现/运行 score probe，构造一次不转置的反例 | 行列语义与特征维度错误 | 能解释 `scores[i,j]` |
| 2 | `02-stable-softmax` | 先预测极端值与 axis 变体，再实现 stable softmax | 非有限输出、行和不为 1、axis 错误 | 性质检查和解释均通过 |
| 3 | `03-value-read` | 只改变一行 V，预测 scores、weights、output 哪些改变 | 把 V 当作权重或错误读取维度 | 预测与观察一致 |
| 4 | `04-qkv-projection` | 实现投影组件并验证输入边界、shape、不可变性 | shape/边界/原地修改错误 | 公开性质测试通过且能解释职责 |
| 5 | `compose-attention` | 只组合 projection、score、softmax、value-read 四个公共组件 | 数据流顺序或组件接口错误 | 端到端性质和组件调用检查通过 |
| 6 | `inspect-and-diagnose` | 注入一次真实错误，使用 inspector 解释原因；完成变体预测 | 只描述现象、没有根因或迁移 | 失败→假设→验证→修复链条完整 |

每一个 Gate 的共同循环为：**先预测 → 运行 micro-lab → 保存结果 → 解释机制 → 手动
commit → Agent 判定**。失败时先用 `/revise` 回到当前机制；只有确定为前置缺口时，
才由后续 i+1 路由进入更小的回补任务。

## 7. 验证与完成规则

### micro-lab 的通过不等于完整掌握

- 每个 P0 micro-lab：必须同时有预测、局部测试、机制解释和一个变体/失败证据。
- 每个 P1 micro-lab：必须有一个完整的解释—实践—验证循环，以及一个边界条件。
- 测试失败只说明该机制证据不足；不得直接推断学习者“不会 attention”。
- Agent 的状态迁移仍由 Policy + State Machine 控制；LLM 只能在 criterion 边界内诊断与提示。

### 组装 Gate 的额外约束

1. 不重新实现 `softmax`、projection、score 或 value read。
2. 组合函数必须调用已通过组件的公共接口。
3. 必须提交一次数据流图：`tokens → Q/K/V → scores → weights → output`。
4. 必须在一个变化输入上预测并验证 output 的变化。

### 结构验证

迁移实现后，CI 至少检查：micro-lab 目录完整、README 与测试存在、每个 Gate 的
manifest 路径可解析、每个链接存在、组装任务不绕过公共组件、所有现有 Week 1 测试
和新增局部性质测试通过。

## 8. 完成与下一能力

完成 Week 1 的条件是：四个 P0 机制分别有独立证据；组装 Gate 只复用组件；一次真实
故障被诊断并修复；inspector 在未见过的输入上完成预测—验证。完成后才解锁 causal
mask，并将它作为 score 到 softmax 之间的一个新的 micro-lab，而不是塞进已有大 Lab。

## 实现迁移顺序（确认后执行）

1. 先落地 `00-shape-trace` 与 `01-score-probe`，验证“理论后立即实验”的体验。
2. 抽出 `02-stable-softmax`、`03-value-read`、`04-qkv-projection` 的稳定公共接口与局部测试。
3. 将现有 `scaled_dot_product_attention` 改为仅组合这些接口，并添加组件调用检查。
4. 重写 Week 1 manifest、模板和 Agent 的 Gate 说明；保留已提交旧证据的兼容迁移策略。
5. 以你的 Week 1 实际学习过程做一次端到端验证，再决定是否推广到 Week 2。
