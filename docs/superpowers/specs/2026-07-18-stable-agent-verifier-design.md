# Stable Agent Verifier 设计

## 1. 能力问题与证据边界

能力问题：

> 给定同一份已 commit 的学生回答、同一 rubric 和同一 verifier 版本，系统能否在真实 LLM API 参与判断时始终得到同一组 criterion 结果，并只允许确定性 Policy 改变学习状态？

当前已有证据：

- `GitGuard` 已把回答与附件绑定到 branch、commit SHA 和内容 hash；
- `PolicyEngine` 已能处理 required criterion、证据不足和冲突结果；
- `LearningStateMachine` 已限制合法状态转换；
- `LearningRuntime` 已能脱离 CLI 被 Fake Agent 调用；
- SiliconFlow 官方文档确认 `/chat/completions`、JSON 模式、视觉输入和 function calling 可用；指定模型 `Qwen/Qwen3.6-35B-A3B` 已在模型中心上线。

尚未证明：真实模型能稳定遵守 rubric、输出完整 JSON，或在重复请求时自然返回相同答案。因此稳定性不能依赖模型自律，必须由评估身份、严格校验、追加式记录和缓存复用保证。

用户此前提供的 API Key 不进入实现、命令、日志或测试。该 Key 应撤销并重新生成；新 Key 只通过 `SILICONFLOW_API_KEY` 环境变量读取。

## 2. 判定机制图

| 节点 | 类型 | 当前深度 | 目标深度 | 依赖角色 | 重要性 | 任务层 | 理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rubric contract | contract | D1 | D4 | hard | P0 | T4 | 当前只有简短 checks，无法约束开放回答判定 |
| evidence identity | contract | D3 | D4 | hard | P0 | T4 | 已有 commit/hash，需要纳入完整 evaluation key |
| evaluation idempotency | mechanism-contract | D0 | D4 | hard | P0 | T4 | 同一标准下稳定性的核心 |
| policy authority | contract | D3 | D4 | integration | P0 | T4 | Agent 不得直接写 Gate 状态 |
| model explanation | explanation | D0 | D2 | downstream | P1 | T1 | 理由可帮助学习，但不拥有状态权限 |
| live provider health | operation | D0 | D2 | soft | P2 | T2 | 只需 smoke test，不把网络稳定性伪装成判定稳定性 |

依赖顺序：

```text
rubric contract + committed evidence identity
  -> evaluation key
  -> registry lookup
  -> SiliconFlow criterion evaluation on cache miss
  -> strict schema and evidence validation
  -> PolicyEngine decision
  -> LearningStateMachine transition
```

## 3. 方案选择

不采用 Agent 直接返回 `passed` 或目标 Gate 状态。它开发快，但模型输出漂移会直接污染学习状态。

不在 MVP 使用多模型投票。投票增加成本和延迟，也不能替代 rubric、幂等记录与 deterministic Policy。

采用 criterion-only Agent：模型只对版本化 criterion 给出结构化结果；Evaluation Registry 固定首次有效结果；Policy Engine 独占最终 recommendation；State Machine 独占状态转换。

## 4. 组件与职责

### 4.1 VersionedRubric

新增 `course-manifests/rubrics/week-01.yaml`，首个 MVP 只实现 Gate 0。每条 criterion 必须包含：

```yaml
rubric_id: week-01-gate-0-rubric
version: 1
gate_id: week-01-gate-0
criteria:
  - criterion_id: shape-bridge-complete
    standard: 学生必须给出 Q、K、V、QK^T、weights、weights@V 的闭合 shape 链，并解释 K.T。
    passed_when:
      - 所有 shape 在同一组符号约定下闭合
      - K.T 的转置维度和语义解释一致
    failed_when:
      - shape 链存在明确矛盾
      - 把 K.T 解释成对 V 的转置或其他错误机制
    insufficient_when:
      - 缺少关键 shape
      - 没有解释 K.T
    allowed_failure_modes: [reinforce, diagnose]
```

Rubric 公开判定标准但不包含完整样例答案。Manifest Gate 增加 `rubric_ref` 和 `rubric_version`；加载时校验 Gate ID、criterion ID、版本和 required evidence 一致。

### 4.2 VerificationRequest

可信输入只能由 Runtime 从 Ledger、Manifest 和 committed bytes 构造：

- course ID、phase ID、gate ID；
- evidence ID、answer path、answer content hash 与 committed Markdown；
- committed attachment path、hash 和支持的图片 bytes；
- rubric ID、version、rubric content hash 与 criteria；
- verifier identity。

Agent 不能自己提供 evidence ID、rubric version 或文件 hash。

### 4.3 VerifierIdentity 与 evaluation key

Verifier identity 包含：

- provider：`siliconflow`；
- model：`Qwen/Qwen3.6-35B-A3B`；
- prompt version；
- output schema version；
- generation settings version，包括 `temperature=0`、`enable_thinking=false` 和 max tokens。

`verifier_version` 是这些字段的规范化 hash。`evaluation_key` 是以下字段的规范化 SHA-256：

```text
course_id
gate_id
answer content hash
sorted attachment content hashes
rubric_id + rubric_version + rubric content hash
verifier_version
```

模型别名背后的服务可能变化，因此 `temperature=0` 只能减少首次波动，不能提供稳定性保证。真正保证来自同一 evaluation key 只接受并保存一个首次有效结果。

### 4.4 EvaluationRegistry

Registry 使用现有 `.learning-os/events.jsonl`，不创建第二个状态真相。它读取 `verification_recorded` 事件并按 `evaluation_key` 查找：

- cache hit：返回已存 criterion results，不调用 API、不追加重复评估；
- 新 evidence ID 指向相同内容时追加轻量 `verification_reused` 引用，使新尝试可追溯但不重新评分；
- cache miss：调用 verifier；只有完整合法输出才追加一次 `verification_recorded`；
- 同一 key 若历史出现不同结果：停止自动状态转换并记录冲突，不能选择“最后一次”；
- rubric 或 verifier 版本变化：生成新 key，保留旧记录并允许新评估。

MVP 的稳定性范围是共享同一个 Ledger/Registry 的 Runtime。跨设备或多用户部署需要共享 Registry，明确留到服务化阶段。

### 4.5 SiliconFlowVerifier

使用 OpenAI-compatible Python client 调用：

```text
base_url = SILICONFLOW_BASE_URL，默认 https://api.siliconflow.cn/v1
api_key  = SILICONFLOW_API_KEY，必须来自环境变量
model    = SILICONFLOW_MODEL，默认 Qwen/Qwen3.6-35B-A3B
endpoint = chat.completions
response_format = json_object
temperature = 0
enable_thinking = false
```

文本回答作为 text content。已 commit 且扩展名为 `.png`、`.jpg`、`.jpeg` 或 `.webp` 的附件以 base64 data URL 作为视觉输入；发送前重新核对 bytes hash。PDF 和其他格式在 MVP 不传给模型，对依赖它们的 criterion 返回 evidence unavailable，不能猜测内容。

官方 JSON 模式文档明确要求调用方处理不完整 JSON，因此响应必须经过本地严格校验，不能直接 `json.loads` 后信任。

### 4.6 严格 Agent 输出契约

允许的顶层结构只有：

```json
{
  "criteria": [
    {
      "criterion_id": "shape-bridge-complete",
      "status": "passed | failed | insufficient_evidence",
      "reason": "仅说明与 rubric 的对应关系",
      "evidence_quotes": ["来自提交内容的短引用"],
      "failure_mode": "reinforce | diagnose | null"
    }
  ]
}
```

禁止字段包括 `gate_status`、`recommendation`、`target_gate`、`evidence_refs` 和 `unlocked_capability`。额外字段、重复 criterion、未知 criterion、缺少 required criterion、无效枚举或无法在提交内容中定位的 quote 都使本次响应无效。

可信 `evidence_refs` 由 Runtime 在本地附加，绝不采用模型输出。

## 5. 数据流与状态权限

```text
LearningAgent.evaluate_current
  -> Runtime 确认当前状态是 evidence_pending
  -> 构造 VerificationRequest 和 evaluation_key
  -> EvaluationRegistry.lookup
      -> hit: 复用 criterion results
      -> miss: SiliconFlowVerifier.verify
               -> strict local validation
               -> append verification_recorded
  -> transition evidence_pending -> evaluating
  -> PolicyEngine.decide(gate, criterion results)
  -> LearningStateMachine.apply_decision
  -> append policy_decided + transition_applied
```

Agent 无权调用 `transition` 指定任意 target status。Runtime 只暴露 `evaluate_current()`，其内部固定执行 Registry、Policy 和 State Machine。

## 6. 错误处理

- 缺少 API Key：live 调用明确失败，单元测试不受影响；
- 401/403：记录 credential error，状态保持 `evidence_pending`；
- 429/503/504：允许有限 transport retry；没有合法输出前不建立 evaluation record；
- timeout、空响应、不完整 JSON、schema 越权：记录 `verification_failed`，状态保持 `evidence_pending`；
- 合法的 `insufficient_evidence`：建立 evaluation record，再由 Policy 确定 `ESCALATE`；
- 同一 key 的 Registry 冲突：禁止 Policy 执行并要求人工检查 Ledger；
- 不保存模型隐藏推理，只保存最终 criterion JSON、provider response ID、model、token usage 和版本身份。

## 7. 测试设计

### 7.1 稳定性核心测试

同一 request 第一次让 Fake Verifier 返回全部 passed，配置它第二次将返回 failed。调用两次后断言：

- verifier 实际只调用一次；
- 两次 criterion results 完全相同；
- evaluation key 和 record ID 相同；
- 从同一个 `evidence_pending` 输入状态计算出的 Policy decision 和 transition draft 相同，不重复向同一 session 追加状态转换。

### 7.2 Agent 越权测试

Fake Verifier 返回 `gate_status: passed` 或 `recommendation: pass`。严格 schema 必须拒绝，Ledger 不出现 `policy_decided` 或 PASS transition，状态保持 `evidence_pending`。

### 7.3 标准版本测试

同一 answer hash 使用 rubric v1 和 v2：

- evaluation key 不同；
- verifier 调用两次；
- 两条 `verification_recorded` 都保留；
- 每条状态决策都能追溯到对应 rubric version。

### 7.4 证据与错误测试

覆盖未知/重复/missing criterion、伪造 quote、附件 hash 不匹配、不支持附件、无效 JSON、timeout 和 provider error。所有失败路径都必须证明没有 PASS transition。

### 7.5 SiliconFlow live smoke test

使用 `pytest.mark.live`，仅在 `SILICONFLOW_API_KEY` 存在时运行。测试使用固定的合成 Gate 0 回答，不使用学生真实数据；第一次调用验证 JSON 可解析和 criterion 完整，第二次通过 Registry 命中同一 record，不能再次发起计费 API 请求。该测试不把模型是否判定 passed 作为断言。

## 8. 结构兼容与文件边界

| 角色 | canonical path | 现有模式 | 决定 |
| --- | --- | --- | --- |
| Gate 机器规则 | `course-manifests/week-01.yaml` | canonical | 增加 rubric ref/version，不复制 rubric 正文 |
| rubric | `course-manifests/rubrics/week-01.yaml` | 新角色 | 与 manifest 同属机器规则，禁止放进学生资源 |
| verifier interface | `learning_runtime/verification/protocol.py` | 缺失 | 新增 provider-neutral contract |
| evaluation registry | `learning_runtime/verification/registry.py` | Ledger canonical | 复用 EventLedger，不建平行数据库 |
| SiliconFlow adapter | `learning_runtime/verification/siliconflow.py` | 缺失 | provider 细节隔离在一个文件 |
| orchestration | `learning_runtime/runtime.py` | canonical | 增加 `evaluate_current()`，不把流程放回 CLI |
| deterministic tests | `tests/learning_runtime/test_stable_verifier.py` | canonical | 默认 CI，无网络 |
| live test | `tests/live/test_siliconflow_verifier.py` | 新例外 | 通过 marker 与环境变量显式隔离 |
| credential template | `.env.example` | 缺失 | 只列变量名；`.env` 加入 gitignore |

跨 Gate 契约保持一条 criterion 一个结果；Gate 0 是首个实现。Gate 1–6 在 rubric 未定义时必须返回“verifier unavailable for gate”，不能退回无标准自由判断。

## 9. 适用范围与非目标

MVP 适用于 Gate 0 的 Markdown 与常见图片附件，验证 criterion-only 判定、稳定缓存和状态权限。它不证明模型评分绝对正确，只证明模型不能绕过标准和重复漂移状态。

本阶段不做：

- 全部七个 Gate 的 rubric；
- 多 Agent 投票；
- OCR 专用服务；
- 跨设备共享 Registry；
- prompt 个性化和 Coach 对话；
- 自动修改学生文件或 Git；
- 将一次 live smoke 的结果作为课程质量结论。

## 10. 完成条件与下一能力

完成条件：

- Fake Verifier 稳定性、越权、版本变化和错误测试全部通过；
- SiliconFlow adapter 能在有环境变量时完成一次 live smoke；
- 同一 key 的第二次评估零 API 调用；
- 任意无标准、无证据或无效输出都无法产生 PASS；
- 每次状态变化可追溯到 evidence、rubric、verifier、criterion results 和 Policy decision；
- API Key 不进入 Git 历史、测试输出或事件 Ledger。

下一步解锁：为 Gate 1–6 逐一编写版本化 rubric，并把 Coach/Diagnostician 建立在已验证 criterion results 上，而不是让对话模型猜测学习状态。

## 11. 官方接口依据

- SiliconFlow Chat Completions：<https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions?playground=open>
- SiliconFlow JSON 模式：<https://docs.siliconflow.cn/cn/userguide/guides/json-mode>
- SiliconFlow 视觉输入：<https://docs.siliconflow.cn/en/userguide/capabilities/vision>
- SiliconFlow Function Calling：<https://docs.siliconflow.cn/cn/userguide/guides/function-calling>
- SiliconFlow 模型中心：<https://www.siliconflow.cn/models>
