# Terminal Learning Agent MVP 设计

## 1. 能力问题与证据边界

唯一能力问题：

> 学生能否通过一个终端入口，在受限 LLM Agent 引导下稳定完成“理解任务—独立作答—手动 commit—提交验证—获得反馈—进入下一步”的 Gate 0 学习闭环？

已有证据：

- `LearningRuntime` 已提供 `start_session()`、`next_action()`、`submit_answer()`、`get_state()` 和 `evaluate_current()`；
- `GitGuard` 已把学生证据绑定到 branch、commit SHA 和内容哈希；
- Stable Verifier 已用版本化 rubric、严格输出校验和 evaluation registry 固定判定；
- `PolicyEngine` 独占 recommendation，`LearningStateMachine` 独占合法状态转换；
- Event Ledger 已支持追加式记录和重放恢复；
- SiliconFlow/Qwen 已有 provider adapter，凭据只从环境变量读取。

尚未证明：学生能否仅凭一个入口完成闭环；对话模型失败或产生越权文本时是否完全不影响学习状态；终端进程退出后是否能恢复相同动作；真实对话是否会在提交前泄露解法。

MVP 只证明 Gate 0 的完整闭环，不证明 Gate 1–6 的 rubric 完整性，也不证明多 Agent、长期学习画像或开放式教学能力。

## 2. 能力节点与强度

| 节点 | 类型 | 当前深度 | 目标深度 | 依赖角色 | 重要性 | 任务层 | 强度理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| command authority | contract | D0 | D4 | hard | P0 | T4 | 自然语言绝不能隐式触发提交或状态变化 |
| grounded presentation | integration | D0 | D3 | hard | P0 | 对话必须由最新 `ActionContract` 和状态构造，不能发明任务 |
| closed-loop orchestration | mechanism | D1 | D4 | integration | P0 | 必须串起 start/resume、submit、verify、policy 和 transition |
| restart recovery | operation | D2 | D4 | hard | P1 | 终端 Agent 不应依赖进程内聊天历史恢复学习进度 |
| provider degradation | diagnosis | D1 | D3 | corequisite | P1 | 对话或判定 API 失败时必须保持可信状态并给出单一恢复动作 |
| conversational style | contract | D0 | D2 | downstream | P2 | 需要友好清晰，但措辞不参与状态判定 |

三个 P0 节点构成最小闭环。对话自由度、个性、长期记忆和多角色协作不进入本阶段，避免用更多模型行为扩大状态不确定性。

## 3. 依赖图、范围与非目标

```text
EventLedger + Manifest + GitGuard + StableVerifier
                     │
                     v
              LearningRuntime
                     │
          +----------+-----------+
          |                      |
          v                      v
DeterministicCommandRouter   ConversationPresenter
          |                      |
          |                SiliconFlow/Qwen
          +----------+-----------+
                     v
               Terminal Agent REPL
```

范围：

- 新入口 `uv run learning-os agent week-01`；
- 持续运行的终端 REPL；
- 自动创建或恢复 session；
- 本地确定性命令 `/submit`、`/status`、`/next`、`/help`、`/quit`、`/retry`；
- Qwen 只负责当前任务解释和提交后反馈；
- 对话 provider 失败时使用确定性模板降级；
- Gate 0 的完整端到端测试和可选 live smoke test。

非目标：

- Gate 1–6 rubric、grader adapter 或课程内容扩写；
- 提交前苏格拉底提示、答案生成或开放式答疑；
- tool-calling、自主工具选择或自然语言动作识别；
- 多 Agent、长期聊天记忆、学习画像、Web UI、账户和云端部署；
- 自动编辑答案、创建分支、commit、push 或后台监控文件。

## 4. 架构与权限边界

### 4.1 AgentCLI

`learning-os agent week-01` 启动 REPL。它负责终端输入输出、进程生命周期和退出码，不拥有课程状态逻辑。

启动时：

1. 检查环境和 student branch；
2. Ledger 不存在时调用 `start_session()`；
3. Ledger 已存在时调用 `get_state()` 与 `next_action()`；
4. 展示当前任务并进入输入循环。

### 4.2 DeterministicCommandRouter

Router 在本地精确匹配斜杠命令。普通文本永远路由到 Presenter，不能转换成动作；“我做完了”“请提交”等自然语言也不能触发 `/submit`。

| 命令 | 行为 | 是否写状态 | 是否调用模型 |
| --- | --- | --- | --- |
| `/submit` | 提交当前已 commit 证据并立即判定 | 是，经 Runtime | Verifier + 成功后的 Presenter |
| `/retry` | 仅在 `evidence_pending` 重试判定 | 可能，经 Runtime | Verifier + 成功后的 Presenter |
| `/status` | 展示可信状态 | 否 | 否 |
| `/next` | 重新展示唯一动作 | 否 | Presenter；失败时模板降级 |
| `/help` | 展示命令与边界 | 否 | 否 |
| `/quit` | 安全退出 | 否 | 否 |

未知斜杠命令返回本地帮助，不发送给模型。

### 4.3 ConversationPresenter

Presenter 使用与 Verifier 相同的 SiliconFlow provider 和 Qwen model，但具有独立 prompt、输入类型和调用路径。它没有 Runtime、Ledger、Git 或 tool-calling 能力。

每次请求从可信状态重新构造，不使用长期聊天历史。允许输入只有：

- 当前 Gate 的 `ActionContract` 投影；
- 当前状态和允许动作的公开摘要；
- 当前 rubric 的公开标准摘要；
- 学生最后一条普通文本，或提交后的可信 `TransitionDecision` 摘要；
- 禁止代答、禁止关键中间结果、禁止宣称状态变化的固定策略。

输出是纯显示文本。Runtime 不解析、存储或使用该文本决定状态。普通对话只解释任务目标、提交要求和操作方式；学生索要答案时，Presenter 重申边界和当前可执行动作。

### 4.4 权限不变量

```text
对话 LLM 没有状态工具
  -> 对话输入不包含可伪造的状态动作
  -> 对话输出不进入 Runtime
  -> 所有写状态动作仍只能经过 LearningRuntime
```

- Verifier 只输出 criterion results；
- Presenter 只输出显示文本；
- CommandRouter 只调用白名单 Runtime 方法；
- PolicyEngine 独占 recommendation；
- State Machine 独占 transition；
- Event Ledger 独占可恢复历史；
- 学生独占答案编辑、分支创建和 Git commit。

Prompt 是辅助边界，不是权限边界。即使 Presenter 输出“已经通过”或伪造命令，程序也只会把它当文本显示。

## 5. 数据流

### 5.1 启动或恢复

```text
agent week-01
  -> SessionController 检查 Ledger
  -> start_session() 或 get_state()
  -> next_action()
  -> Presenter.render_action()
  -> 输出任务并等待输入
```

Presenter 失败时，使用 `ActionContract` 的确定性本地模板继续运行。

### 5.2 普通文本

```text
student text
  -> Router 分类为 presentation-only
  -> 重新读取 state + next_action
  -> Presenter.render_explanation(last_message, trusted_context)
  -> 输出文本
```

该路径不写 Ledger、不调用 Verifier、不执行状态转换。

### 5.3 `/submit`

```text
/submit
  -> submit_answer(current_gate)
     -> 检查 answer、附件和 committed snapshot
     -> append evidence + transition to evidence_pending
  -> evaluate_current(verifier)
     -> registry lookup 或 SiliconFlow criterion evaluation
     -> strict validation
     -> PolicyEngine decision
     -> State Machine transition
  -> Presenter.render_feedback(trusted receipt)
  -> 若已推进，展示下一 ActionContract
```

`/submit` 是一个用户动作，但内部保持两个可信阶段。若提交检查失败，不调用任何模型；若提交成功但判定 provider 失败，证据仍保留并停在 `evidence_pending`。

### 5.4 `/retry`

`/retry` 仅在 `evidence_pending` 调用 `evaluate_current()`。已有合法 evaluation record 时复用；没有合法记录时重新请求 provider。其他状态确定性拒绝该命令。

## 6. 错误处理与恢复

| 故障 | 状态行为 | 学生看到的唯一动作 |
| --- | --- | --- |
| 空白、缺附件、未 commit | 保持当前 active Gate | 完成缺项并手动 commit 后 `/submit` |
| Presenter 缺 key、超时或无效响应 | 状态不变 | 阅读本地模板并继续，或稍后 `/next` |
| Verifier 缺 key 或 provider 失败 | 保持 `evidence_pending` | 配置/恢复 provider 后 `/retry` |
| Verifier 非法 JSON 或越权字段 | 保持 `evidence_pending`，记录失败 | `/retry` 或人工检查日志 |
| 合法 `insufficient_evidence` | 由 Policy 确定返工/升级，不得 PASS | 按可信缺证据反馈执行 |
| 未知命令 | 状态不变 | `/help` |
| Ledger 损坏 | 停止启动，不猜测状态 | 根据报告的行号人工修复 |
| Ctrl-C 或 `/quit` | 不写伪状态 | 再次运行同一入口自动恢复 |

错误消息不能包含 API key、完整 provider response、隐藏 grader 或内部 prompt。对话模型错误与判定模型错误分开报告，不能把“反馈生成失败”描述成“判定失败”。

## 7. 结构兼容与跨阶段合约

### 7.1 结构兼容图

| 角色 | canonical path | 现有模式 | 决定与影响 |
| --- | --- | --- | --- |
| CLI 入口 | `learning_runtime/cli.py` | canonical | 增加 `agent` 子命令，不创建第二套 executable |
| Agent orchestration | `learning_runtime/agent/session.py` | 新角色 | 只编排 Router、Presenter、Runtime |
| command contract | `learning_runtime/agent/commands.py` | 新角色 | 纯本地解析，可独立测试 |
| conversation protocol | `learning_runtime/agent/protocol.py` | 参照 verification protocol | provider-neutral presenter contract |
| SiliconFlow presenter | `learning_runtime/agent/siliconflow.py` | 参照 verifier adapter | 复用配置约定，隔离 prompt 与输出 |
| deterministic fallback | `learning_runtime/agent/presenter.py` | 新角色 | 从 typed context 生成本地文本 |
| Runtime authority | `learning_runtime/runtime.py` | canonical | 只补必要 retry/query 接口，不搬迁状态逻辑 |
| Agent tests | `tests/learning_runtime/test_agent_session.py` | canonical | 默认无网络的端到端闭环 |
| live conversation test | `tests/live/test_siliconflow_agent_live.py` | 已有 live 例外 | marker + env 隔离 |
| learner evidence | `homework_answer/week-01/` | canonical | Agent 不改变所有权或格式 |

### 7.2 跨阶段合约

| 字段 | 分类 | 本阶段决定 |
| --- | --- | --- |
| 课程导航、资源、任务、Lab 路径 | canonical | 不改变 |
| student answer 路径与 Markdown/附件粒度 | canonical | 不改变 |
| `ActionContract` | canonical | Presenter 的唯一任务输入，不复制课程正文 |
| Event Ledger evidence fields | canonical | 不加入聊天文本 |
| slash command set | justified variation | Agent 专属交互合约，命令名稳定且写入文档 |
| conversation transcript | explicit non-artifact | MVP 不保存，不作为学习证据 |
| provider config | canonical | 继续使用 `SILICONFLOW_API_KEY/BASE_URL/MODEL` |

不迁移现有课程文件，不创建并行 `agent-state` 数据库，不把 REPL transcript 当作掌握证据。

## 8. 知识门控实施链

1. 定义 typed conversation context、Presenter protocol 和本地 fallback；先证明文本输出不能反向进入状态。
2. 实现精确 CommandRouter；用表驱动测试证明普通文字与未知命令无动作权。
3. 实现 SessionController 的自动 start/resume 和确定性命令处理，不接真实模型。
4. 以 Fake Presenter + Fake Verifier 在临时 Git 仓库打通 Gate 0。
5. 接入 SiliconFlow Presenter，并验证 provider 失败时本地降级。
6. 暴露 `learning-os agent week-01`，补使用文档和可选 live test。

后一步必须消费前一步的 typed contract，不能在 CLI 中重新实现 Runtime 状态规则。

## 9. 验证与完成 Gate

### 9.1 命令权限

- 普通文字不会调用 submit、evaluate 或 Ledger append；
- 只有精确 `/submit` 能进入提交流程；
- `/status`、`/next`、`/help` 不写状态；
- 对话文本包含“passed”或伪造命令时状态仍不变；
- Agent 不执行 Git 写操作。

### 9.2 完整闭环

在真实临时 Git 仓库模拟：

```text
自动 start
  -> 学生填写但未 commit
  -> /submit 被拒绝
  -> 学生手动 commit
  -> /submit + Fake Verifier
  -> Policy/State Machine 推进
  -> 显示下一 ActionContract
  -> 退出并恢复相同状态
```

### 9.3 稳定与降级

- 相同 evidence/rubric/verifier version 复用同一 evaluation；
- Presenter 措辞变化不影响 state 或 decision；
- Presenter 失败使用本地模板；
- Verifier 失败保持 `evidence_pending` 并允许 `/retry`；
- 非法 Verifier 输出、重复命令和重启均不产生非法或重复 transition；
- 无 key 的默认测试完全离线。

### 9.4 Live smoke

手动 live test 使用固定合成内容，只验证：

- Presenter 返回非空文本；
- Verifier 返回可校验 criterion JSON；
- Registry 复用避免第二次计费判定；
- 不上传真实学生历史或隐藏 grader。

### 9.5 完成条件

MVP 只有在以下条件全部成立时完成：

- 一个终端命令可自动新建或恢复 Gate 0 session；
- 未 commit 证据无法进入判定；
- 学生手动 commit 后可完成 submit、verify、policy、transition；
- 对话 LLM 的失败、越权文本和措辞漂移均不能污染学习状态；
- 中断后从 Ledger 恢复；
- 默认测试离线通过，可选 SiliconFlow live test 可单独运行；
- README 清楚说明命令、权限边界、凭据配置和恢复路径。

未解决的 P0 节点不得以“界面可以运行”代替。特别是只完成 REPL、但普通文字仍可能触发动作，不能视为 MVP 完成。

## 10. 下一步解锁能力

本 MVP 完成后，系统才具备可靠承载教学智能的交互壳。下一阶段优先增加“提交后 Diagnostician”：它消费可信 criterion failure 和 evidence refs，生成分层反馈，但仍不拥有状态权。Gate 1–6 rubric、提交前 Coach、多 Agent 和 Web UI 继续后置，分别设计和验证。
