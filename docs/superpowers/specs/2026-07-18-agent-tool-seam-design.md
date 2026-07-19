# Agent Tool Seam 设计

## 目标

用一个确定性的 Fake Agent 接管测试证明：学习状态内核不依赖 CLI，可以被未来的 LLM Agent 作为工具调用。这个里程碑不再验证学习方法本身，也不增加新的课程状态。

测试通过即表示项目从“CLI 驱动的状态机”进入“Agent 可调用的 Runtime”；它仍不表示已经接入真实模型或能够判断开放回答质量。

## 最小架构

增加一个无打印、无命令行参数的应用服务 `LearningRuntime`，向调用者提供四个稳定入口：

- `start_session(phase)`：验证学生分支、初始化当前 Gate 作答文件并创建 session；
- `next_action()`：返回结构化 `ActionContract`；
- `submit_answer(gate_id)`：验证作答结构与 Git commit，记录证据并推进到 `evidence_pending`；
- `get_state()`：从 Ledger 重放并返回 `LearnerState`。

`cli.py` 降级为薄适配器，只负责解析参数、调用 `LearningRuntime` 和打印返回值。Fake Agent 与未来真实 Agent 调用同一个 `LearningRuntime`，不调用 CLI 私有函数，也不解析终端文本。

## 接管测试

新增一个端到端测试 `test_fake_agent_drives_runtime_without_cli`：

1. 在临时课程仓库建立学生分支；
2. Fake Agent 调用 `start_session`，获得 Gate 0 与作答路径；
3. 测试中的“学生模拟器”填写 Markdown、添加手写附件并手动执行 Git commit；
4. Fake Agent 调用 `submit_answer`；
5. 断言返回状态为 `evidence_pending`；
6. 断言 Ledger 包含 branch、commit SHA、作答 hash 与附件 hash；
7. 断言整个流程没有调用 CLI `main`，也没有由 Runtime 执行 Git 写操作。

Fake Agent 只做固定决策：读取结构化 action，并选择调用允许的下一个工具。它不是模拟教学智能；它的唯一用途是验证工具边界可被 Agent 接管。

## 数据流

```text
Fake Agent
  -> LearningRuntime.start_session
  -> ActionContract
  -> 学生填写并手动 commit
  -> LearningRuntime.submit_answer
  -> GitGuard + AnswerWorkspace
  -> EventLedger
  -> LearningStateMachine
  -> LearnerState(evidence_pending)
```

CLI 和未来 LLM Agent 都处在 `LearningRuntime` 外部，因此替换交互层不会改写课程规则、证据来源或状态权限。

## 错误与安全边界

- 保护分支、空白答案、缺失附件和未 commit 作答在写入尝试事件前失败；
- Runtime 与 Fake Agent 都不得执行 `git add`、`git commit`、`git switch` 或 `git push`；
- Fake Agent 不可以把 `evidence_pending` 宣称为通过；
- 本里程碑不调用真实模型、不需要 API key、不引入网络依赖；
- CLI 现有行为保持兼容，由原有端到端测试继续保护。

## 完成标准与下一阶段

本里程碑完成时必须满足：

- 新 Fake Agent 接管测试先失败、后通过；
- 原有测试全部通过；
- CLI 通过 `LearningRuntime` 工作，而不是维护第二份流程；
- 文档明确区分 Runtime、Fake Agent 和真实 LLM Agent。

完成后，下一阶段直接构建 Agent v0：把真实模型接到同一组结构化工具，加入 tool-call 循环和最小 Verifier。不会继续扩写当前 CLI 状态机。
