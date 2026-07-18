# Self-Learning Runtime MVP 设计

## 1. 决策摘要

`transformer-from-scratch-lab` 是 Learning OS 学习理念的第一份真实参考实现，
也是 Self-Learning Agent 的首个 MVP 试验场。第一版不新建通用平台，而是在
本仓库现有课程契约之上增加一个最小运行层，验证系统能否在不替学生完成练习
的前提下，根据真实证据驱动下一步学习。

MVP 的核心不是“多个 AI 老师”，而是一个 **证据门控的学习状态机**：

```text
目标 -> 主动任务 -> 学生尝试 -> 证据验证 -> 缺口诊断
     -> 补强/回退 -> 再尝试 -> 独立迁移 -> 解锁
```

Multi-Agent 只承担调度、练习和诊断三种逻辑职责。Agent 可以提出建议，但
不能自行把学生标记为掌握；状态转换由确定性规则执行。

首个纵向切片复用 Week 0 与 Week 1 的真实能力链：

```text
矩阵 shape -> stable softmax -> scaled dot-product attention
            -> attention 故障诊断 -> 独立迁移
```

该切片稳定后，再决定是否把通用运行层抽取成独立项目。

## 2. 产品问题与目标用户

### 2.1 能力问题

> 对一个具有明确知识依赖和可验证产物的 Transformer P0 机制，系统能否在
> 不泄露实现答案的前提下，根据学生的推导、代码、测试、失败记录和迁移结果，
> 正确决定通过、补强、诊断或升级，并让学生完成一次独立迁移？

### 2.2 目标用户

MVP 面向满足以下条件的学习者：

- 具有较强自驱力，愿意独立完成推导、代码和复盘；
- 希望理解 Transformer 的机制、shape、数值稳定性和数据流；
- 接受按证据推进，而不是按时间或“看完材料”推进；
- 能在本地使用 Python、`uv`、pytest 和命令行；
- 接受 AI 不在首次尝试前提供完整答案。

### 2.3 当前证据与保留意见

已有证据：

- 仓库已经将导航、资源、任务链、Lab 和 hidden grader 分离；
- Week 0 与 Week 1 已有明确的知识依赖、P0 Gate 和回退条件；
- grader 已能返回 `shape`、`数值稳定性`、`公式`、`边界输入` 等失败类别；
- 课程规则已明确要求预测、实现、失败解释和独立迁移。

仍未证明：

- Agent 能否把 grader 结果可靠映射到真实知识缺口；
- 学生是否会因分层提示而提高独立尝试和迁移能力；
- Multi-Agent 的职责隔离是否优于一个模块化单 Agent；
- 开放式概念回答能否被稳定评价；
- 长期复习与跨课程推荐如何消费本轮证据。

未知知识深度必须记录为 `unknown`，不能推断为掌握或失败。

## 3. 方案比较与选定方向

### 3.1 方案 A：立即建设独立通用 Runtime

优点：课程与引擎边界最干净，未来可以接入多门课。

缺点：在没有真实运行数据前容易抽象错误；需要同时维护两个仓库、适配协议和
版本兼容；失败时难以区分是课程问题还是 Runtime 问题。

### 3.2 方案 B：在本仓库完成纵向切片，验证后抽取

优点：直接复用真实课程、grader 和学生产物；能最快观察学习行为；减少协议与
部署工作；通用接口可以从真实重复模式中产生。

缺点：早期实现会带有 Transformer 课程上下文；抽取时需要重新检查哪些规则
真正通用。

### 3.3 方案 C：只扩展 grader，不建设运行层

优点：实现最小，确定性强。

缺点：只能告诉学生代码是否通过，无法读取概念证据、管理提示、记录学习状态、
执行回退或支持独立迁移，不构成完整学习循环。

### 3.4 决策

采用方案 B。第一版在本仓库中增加最小 Learning Runtime，但保持课程定义、
学生产物、hidden grader 和运行状态之间的路径及权限边界。达到抽取门槛后再
建立独立通用项目。

## 4. MVP 知识图与强度分配

本表描述 Runtime 首轮必须正确驱动的学习节点，而不是重新设计 Week 1 内容。

| 节点 | 类型 | 当前 -> 目标 | 依赖角色 | 优先级与理由 | 任务层 |
| --- | --- | --- | --- | --- | --- |
| 矩阵 shape 与乘法契约 | mechanism + contract | 由 Week 0 证据决定 -> D3 | hard | P0：所有 attention shape 的直接前置 | T1 检索；缺证据时回退 Week 0 |
| stable softmax | mechanism + diagnosis | unknown -> D4 | hard | P0：数值稳定性和 axis 决定权重合法性 | T1 -> T4 |
| score、缩放与 Q/K 语义 | mechanism | unknown -> D4 | hard | P0：决定匹配分数的因果解释 | T1 -> T4 |
| `weights @ V` | mechanism | unknown -> D4 | hard | P0：定义内容读取和输出 shape | T1 -> T4 |
| 单头 attention 组合 | integration | 未组合 -> D4 | integration | P0：MVP 的端到端学习能力 | T3 -> T5 |
| 失败分类与假设验证 | diagnosis | unknown -> D4 | corequisite | P1：用于区分概念、实现和环境问题 | T4 |
| attention inspector | integration + procedure | unknown -> D3 | downstream | P1：证明未复制 Lab 的独立迁移 | T5 |
| causal mask | orientation | D0 -> D1 | downstream | P3：只作为解锁后的下一能力 | T0 |

P0 节点必须包含多种证据：预测、解释、受约束实现、失败或变式、迁移与回访。
P3 节点不新增 Lab。

### 4.1 依赖图

```text
Week 0 shape 证据
  -> Q/K/V 与 score 语义
  -> stable softmax
  -> weights @ V
  -> 单头 attention 组合
  -> 故障诊断
  -> attention inspector 独立迁移
  -> 解锁 causal mask 课程设计
```

## 5. 系统边界与架构

### 5.1 五类边界

```text
课程定义 != 运行状态
学生产物 != Agent 生成内容
原始证据 != Agent 推断
诊断建议 != 状态转换
hidden grader != Coach 上下文
```

### 5.2 逻辑架构

```text
现有课程文件（只读规则）
  -> Course Manifest Adapter
  -> Deterministic Learning State Machine
      -> Coordinator：选择当前可执行 Gate
      -> Coach：给任务与受限提示
      -> Evidence Collector：读取学生产物和命令结果
      -> Verifier：执行确定性检查
      -> Diagnostician：提出缺口和路由建议
      -> Policy Engine：验证建议是否符合课程门槛
  -> Evidence Ledger 与 Learner State
  -> 唯一下一步任务或升级请求
```

### 5.3 组件职责

#### Course Manifest Adapter

用途：把现有 Markdown 课程契约连接到机器运行层。

输入：`weeks/`、`tasks/`、`resources/`、`labs/` 中的稳定路径，以及一个轻量
machine-readable manifest。

输出：Gate、知识节点、依赖、所需证据、允许转换和产物路径。

约束：manifest 只保存机器需要的关系和引用，不复制课程正文，不成为第二份
课程内容真相。

#### Learning State Machine

用途：保存当前 Gate、尝试次数、已验证证据、提示层级和解锁状态。

输入：当前状态、课程规则、Policy Engine 判定。

输出：合法状态转换和下一可执行 Gate。

约束：只有状态机可以写 Gate 状态；状态机本身不调用 LLM 做自由判断。

#### Coordinator

用途：把当前状态压缩为一次清楚的学习行动。

输入：状态机提供的可执行 Gate、历史证据摘要和允许权限。

输出：交给 Coach、Verifier 或 Diagnostician 的结构化子任务。

约束：不能改变目标、降低 P0 门槛、跳过依赖或修改学生代码。

#### Practice Coach

用途：提出检索题、预测、变式和分层提示。

输入：当前 Gate、公开课程材料、学生已提交的尝试、当前提示等级。

输出：一个下一步练习或一个允许等级内的提示。

约束：看不到 hidden tests 和参考实现；不能写入 Lab 实现；首次尝试前不得给
完整解法。

#### Evidence Collector

用途：收集而不解释事实。

输入：学生答案文件、Lab 文件、公开测试输出、grader 输出、命令退出码。

输出：带来源、时间、hash 和类型的 Evidence Record。

约束：不把缺失文件解释成不会；不修改原始产物；命令执行必须使用 allowlist。

#### Verifier

用途：用确定性检查和逐项 rubric 判断证据是否满足条件。

输入：Evidence Record、Gate 验收标准、grader adapter。

输出：每个 criterion 的 `passed`、`failed` 或 `insufficient_evidence`。

约束：不决定学习路线；开放式回答不能只返回一个总分。

#### Diagnostician

用途：把验证失败映射到可能的知识缺口和回退节点。

输入：criterion 结果、相关原始证据、知识依赖图。

输出：`PASS`、`REINFORCE`、`DIAGNOSE` 或 `ESCALATE` 建议，附证据引用、
原因和回退目标。

约束：只能提出建议；不得修改状态或学生文件。

#### Policy Engine

用途：用确定性规则审查诊断建议。

输入：诊断建议、Gate 必需证据、依赖状态和权限规则。

输出：允许转换、拒绝转换或要求人工确认。

约束：证据冲突、缺少 P0 必需证据或目标歧义必须 `ESCALATE`。

#### Evidence Ledger

用途：保存可追溯学习历史。

记录类型：`assignment`、`attempt`、`observation`、`evaluation`、
`diagnosis`、`decision`、`hint`、`transition` 和 `escalation`。

约束：事件追加写入，不原地改写历史；修正使用新事件；每个推断和决定都引用
原始证据 ID。

## 6. 仓库结构与兼容性

### 6.1 现有课程契约

| 产物角色 | 规范路径 | 当前模式 | 分类 | MVP 决策 |
| --- | --- | --- | --- | --- |
| 周导航 | `weeks/week-XX/README.md` | Week 0/1 均存在 | canonical | 不改变；Runtime 只读取入口和完成定义 |
| 学习资源 | `resources/week-XX/` | Week 0/1 均为分角色文件 | canonical | 不移动；答案证据只引用路径 |
| 任务链 | `tasks/week-XX.md` | Gate 与解锁条件已显式 | canonical | 继续作为人类可读真相 |
| 可运行 Lab | `labs/week-XX/` | starter、smoke test、grader 入口 | canonical | 不改变运行入口 |
| hidden grader | `.grader/week_XX.py` | 本地、gitignore | canonical private | Verifier 只能读取分类结果，不暴露代码 |
| 学习者答案 | `homework_answer/` 或课程约定的 answers/notes | 本地已有但未形成公开稳定契约 | incomplete | MVP 显式配置路径，不自动提交 |
| 运行状态 | 尚无 | 尚无 | new role required | 使用 `.learning-os/`，保持本地私有 |
| 机器 Gate 契约 | 尚无 | Markdown 对机器不稳定 | new role required | 使用 `course-manifests/week-01.yaml`，只保存引用和规则 |

### 6.2 新增路径

```text
learning_runtime/
  cli.py
  coordinator.py
  state_machine.py
  policies.py
  schemas.py
  agents/
    coach.py
    diagnostician.py
  evidence/
    collector.py
    verifier.py
    grader_adapter.py
  storage/
    event_ledger.py
    learner_state.py

course-manifests/
  week-01.yaml

tests/
  learning_runtime/
    test_state_machine.py
    test_policies.py
    test_evidence_collector.py
    test_seeded_failures.py
    test_end_to_end_week_01.py

.learning-os/                  # gitignored runtime data
  state.json
  events.jsonl
  evaluations/
```

### 6.3 为什么需要新角色

- 现有 `tasks/` 适合人阅读，但自由 Markdown 不足以稳定承载机器依赖、证据 schema
  和转换规则；manifest 因此是新的机器契约，而不是第二套任务内容。
- 现有 `labs/` 属于学习者练习，不应保存运行引擎或全局状态。
- 现有 `docs/` 只保存说明，不能充当可恢复的运行状态。
- `.learning-os/` 包含个人尝试、诊断和模型输出，默认必须私有且可删除重建。

### 6.4 跨阶段格式契约

MVP 只为 Week 1 创建 manifest，但 schema 必须允许 Week 0 作为回退目标。每个
未来 manifest 统一包含：

```text
course_id
phase_id
capability_question
knowledge_nodes
gates
dependencies
artifact_refs
evidence_requirements
allowed_hint_levels
failure_routes
completion_rule
next_capability
```

每个 Gate 统一包含：

```text
gate_id
knowledge_node_ids
task_layer
required_evidence
verifier
pass_rule
rollback_target
escalation_conditions
```

链接使用仓库根目录相对路径；测试和 grader 命令必须直接引用现有入口；manifest
验证必须检查引用文件存在、Gate ID 唯一、依赖无环、回退目标存在和必需字段
齐全。

## 7. 状态、证据和决策模型

### 7.1 Learner State

```yaml
course_id: transformer-from-scratch
phase_id: week-01
current_gate: week-01-gate-3
gate_status: active
attempt_count: 2
hint_level: 1
verified_evidence_ids:
  - evidence-0012
unresolved_p0_nodes:
  - stable-softmax
last_event_id: event-0041
```

状态是可由 Ledger 重放得到的缓存；Ledger 是审计真相。

### 7.2 Evidence Record

```yaml
evidence_id: evidence-0012
type: grader_result
source: .grader/week_01.py
artifact_ref: labs/week-01/src/attention.py
observed_at: 2026-07-18T10:00:00+08:00
content_hash: sha256:4f6c61e85f754d8f0f8d0c142f3c57e18dd6ae6f3f5acb62bb8b3d62f02db842
observation:
  exit_code: 1
  category: numerical-stability
  gate: 1
```

`observation` 只保存可观察事实。Agent 的解释必须进入单独的 diagnosis event。

### 7.3 Evaluation Result

```yaml
criterion_results:
  - criterion_id: stable-softmax-finite-output
    status: failed
    evidence_refs: [evidence-0012]
  - criterion_id: row-sums-equal-one
    status: insufficient_evidence
    evidence_refs: []
```

### 7.4 Transition Decision

```yaml
recommendation: reinforce
target_gate: week-01-gate-3
failed_node: stable-softmax
reason: extreme scores produced non-finite weights
evidence_refs: [evidence-0012]
policy_result: allowed
next_action: run the bounded extreme-value prediction exercise
```

## 8. 端到端数据流

1. Runtime 加载 `course-manifests/week-01.yaml`，验证 schema、路径、依赖和命令。
2. Ledger 不存在时创建本地 session；存在时重放事件恢复 Learner State。
3. State Machine 根据已验证依赖选择唯一当前 Gate。
4. Coordinator 生成结构化任务合同，Coach 将其表达为一个主动练习。
5. 学生完成推导、预测或代码，并显式发起 `submit`；系统不持续监控编辑过程。
6. Evidence Collector 对允许路径生成 hash，执行 allowlist 中的 public test 或
   grader 命令，记录原始输出、退出码和失败类别。
7. Verifier 对 Gate 的每项 criterion 产生逐项结果。
8. Diagnostician 引用 criterion 和原始证据，提出转换建议。
9. Policy Engine 检查 P0 必需证据、依赖、提示策略和升级条件。
10. State Machine 执行合法转换，Ledger 追加 decision 与 transition 事件。
11. Runtime 输出一个下一动作、当前原因和可下钻的证据索引。
12. 独立迁移通过后，Week 1 才完成并解锁 causal mask 的下一阶段设计。

## 9. 状态转换

```text
READY -> ACTIVE -> EVIDENCE_PENDING -> EVALUATING
  -> PASSED
  -> REINFORCEMENT_REQUIRED -> ACTIVE
  -> DIAGNOSIS_REQUIRED -> ACTIVE
  -> ESCALATED
```

四种面向学生的决策：

| 决策 | 触发条件 | 系统动作 |
| --- | --- | --- |
| PASS | 所有 P0 必需 criterion 有独立证据且依赖已满足 | 记录证据并解锁下一 Gate |
| REINFORCE | 缺口明确指向已知前置节点 | 回退到指定节点，安排一个最小补强任务 |
| DIAGNOSE | 结果失败但多个原因仍可成立，或目标是诊断能力 | 保持 Gate，要求提出假设和区分实验 |
| ESCALATE | 证据冲突、规则缺失、权限不足、目标歧义或开放评价无法稳定判断 | 停止转换并向学生或课程作者报告 |

任何 `insufficient_evidence` 都不能被自动当成失败或通过。

## 10. 主动学习与防答案泄露策略

### 10.1 主动学习约束

- 每个 Gate 先要求学生预测、解释或提交首次实现；
- 系统只输出一个下一行动，不一次生成整周待办；
- “看完了”“理解了”和会话时长不构成掌握证据；
- Lab 通过后仍要求真实失败解释与独立迁移；
- P0 的后续回访不能由同一次提交满足。

### 10.2 提示阶梯

| 等级 | 允许内容 | 解锁条件 |
| --- | --- | --- |
| L0 | 重述目标、输入输出和禁止项 | 默认 |
| L1 | 指出失败所属知识区域并提出观察问题 | 已提交一次有效尝试 |
| L2 | 给最小反例、要求打印 shape 或比较假设 | 同类失败第二次出现 |
| L3 | 指向具体契约、前置材料或需要验证的性质 | 已记录原因假设和验证尝试 |
| L4 | 完成后的讲评与替代方案比较 | Gate 已通过或人工明确授权 |

MVP 不提供“直接显示完整实现”的路径。Coach 上下文不包含 `.grader/` 源码、
hidden inputs、expected outputs 或 solutions。

## 11. 错误处理与恢复

| 失败 | 处理 |
| --- | --- |
| manifest 缺字段、依赖成环或路径不存在 | 启动失败，报告精确字段；不创建学习状态 |
| grader 不存在 | 标记 verifier unavailable；允许理论任务，但不允许 Lab PASS |
| 命令超时或异常退出 | 记录 operation evidence；分类为环境/工具问题，不推断知识失败 |
| 学生文件缺失 | 返回 insufficient evidence；不生成空答案或替学生创建实现 |
| Agent 输出不符合 schema | 最多重试一次结构化生成；仍失败则 ESCALATE |
| Diagnostician 与规则冲突 | Policy Engine 拒绝转换并记录冲突 |
| Ledger 最后一行损坏 | 停止写入，报告最后有效事件；不得静默覆盖 |
| 状态缓存与 Ledger 不一致 | 由 Ledger 重放恢复缓存 |
| 学生中途退出 | 已完成事件保持；下次从最后一个有效状态恢复 |
| evidence hash 与当前文件不一致 | 将旧证据标记为对应旧版本；要求重新验证当前产物 |

Runtime 不自动执行删除、提交、推送、安装依赖或修改学生代码等高影响操作。

## 12. CLI MVP 交互

第一版只需要以下入口：

```text
learning-os start week-01
learning-os next
learning-os submit --gate GATE_ID
learning-os hint
learning-os status
learning-os evidence EVIDENCE_ID
learning-os resume
```

输出契约：

```text
当前能力：
当前 Gate：
为什么是这一步：
你现在需要完成的一个动作：
提交后会检查什么：
允许的提示等级：
证据索引：
```

普通状态保持简洁；发生升级时输出事实、未知项、可选动作和原始证据索引。

## 13. 测试策略

### 13.1 确定性单元测试

- 状态机只允许合法转换；
- P0 证据缺失时不能 PASS；
- `unknown` 与 `failed` 保持不同；
- 回退目标必须是依赖图中存在的节点；
- Ledger 追加、重放和损坏检测；
- manifest schema、路径和无环验证；
- Coach、Diagnostician 的读写权限策略。

### 13.2 Seeded failure 测试

准备已知根因的 fixture：

- softmax 未减 max，触发数值溢出；
- softmax 使用错误 axis；
- 忘记 `K.T`；
- `weights @ V` shape 或顺序错误；
- 环境缺少 grader；
- 概念解释与代码证据冲突；
- 测试通过但独立迁移失败。

每个 fixture 必须验证：原始证据、criterion 判定、诊断建议、Policy 结果和最终
状态转换，而不只测试最终文本。

### 13.3 端到端场景

至少覆盖：

1. 从 Week 0 证据恢复并进入 Week 1；
2. stable softmax 首次失败；
3. Coach 按提示阶梯给补强任务；
4. 修复后通过 grader；
5. 故障诊断任务通过；
6. attention inspector 独立迁移通过；
7. 重启后状态与证据保持一致；
8. 解锁 causal mask，而不自动创建下一阶段内容。

### 13.4 单 Agent 基线

使用同一课程、同一失败 fixture 和同一模型，对比：

- 模块化单 Agent；
- Coordinator + Coach + Diagnostician；
- 无 Agent、仅 grader 的基线。

比较诊断正确性、答案泄露、错误状态转换、人工介入、调用成本和延迟。若多
Agent 没有带来可测收益，MVP 应收缩为模块化单 Agent，而不是保留角色表演。

## 14. MVP 完成门槛

以下条件必须全部满足：

- Week 1 manifest 可以通过 schema、路径、依赖和命令检查；
- 状态机覆盖 PASS、REINFORCE、DIAGNOSE、ESCALATE；
- 每个转换都引用原始证据，且 Ledger 可重放恢复状态；
- Coach 无法读取 `.grader/` 和 solutions，无法写学生实现；
- seeded failures 能区分机制、实现和环境问题；
- evidence 不足时系统不会猜测掌握状态；
- 一个真实或受控学习 session 完成从失败、补强到迁移的完整循环；
- 重启后可以从最后有效 Gate 继续；
- 现有 `uv run pytest -q` 与 `uv run python labs/week-01/run_grade.py` 入口不被破坏；
- 新增结构通过链接、路径、manifest 格式和测试发现检查；
- 多 Agent 相比基线的价值有数据支持，或明确记录回退为单 Agent 的决定。

完成不能只以 CLI 可运行、Agent 能对话、grader 通过或生成文件数量来判断。

## 15. 适用范围与非目标

### 15.1 MVP 适用

- 单学习者、本地运行；
- 一门已经设计好的 Transformer 课程；
- 具有明确知识依赖和可验证产物的工程学习；
- Python、数学、系统等可用推导、测试、实验和 demo 验证的主题；
- 愿意先尝试、允许系统限制答案泄露的高自驱学习者。

### 15.2 MVP 非目标

- 任意主题自动生成完整课程；
- 自动生成可信 hidden grader；
- Web UI、Dashboard、多用户和云同步；
- 向量数据库或通用知识图谱；
- 职业路径和长期 DNA 式推荐；
- 艾宾浩斯长期复习调度；
- 情绪陪伴、打卡和游戏化；
- 多 Agent 自由群聊；
- 自动修改学生代码、答案或 demo；
- 根据浏览时间或对话流畅度推断掌握。

## 16. 关键未知项与验证顺序

### P0：MVP 必须验证

1. grader 类别是否足以支持知识缺口诊断；
2. 提示等级能否帮助学生而不泄露答案；
3. 哪组证据足以改变 P0 状态；
4. Multi-Agent 是否优于单 Agent 或纯 grader；
5. 学生是否提高首次独立尝试、故障解释和迁移表现；
6. 运行状态与课程 Markdown 漂移时如何被自动发现。

### P1：MVP 后再决定

1. Skill 输出如何自动编译为 Course Manifest；
2. 开放式口述和推导采用 LLM、人工还是混合评价；
3. hidden grader 如何安全分发给外部学习者；
4. Evidence Ledger 如何连接长期复习；
5. Runtime 抽取后的课程版本兼容方式。

### P2：暂不进入设计

Web 产品形态、多用户权限、课程市场、跨领域通用图谱和长期方向推荐。

## 17. 抽取为独立项目的门槛

只有同时满足以下条件，才从本仓库抽取通用 Runtime：

- Week 0/1 至少两个阶段使用同一状态、证据和 manifest schema；
- 至少一次真实学习 session 证明回退与恢复有价值；
- 通用模块中没有硬编码 `attention`、`softmax` 或特定周路径；
- 新课程接入只需要 manifest、verifier adapter 和课程文件，不需要修改状态机；
- 多 Agent 价值已经通过基线实验支持；
- 隐私、grader 隔离和答案泄露边界可测试。

抽取后，本仓库成为第一份标准课程、验收样板和端到端测试夹具，而不是被新的
通用项目替代。

## 18. 下一项解锁能力

MVP 设计通过并完成实现验证后，下一项能力不是立即扩展到任意课程，而是：

> 使用同一 Runtime 和 schema 驱动 causal mask 阶段，验证一套运行契约能否跨
> 两个连续知识阶段复用，并根据真实证据决定保留仓库内实现还是抽取通用项目。
