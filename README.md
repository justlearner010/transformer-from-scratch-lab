# Transformer From Scratch Lab

一个以理论理解为起点的 Transformer 自学实验室：先完成阅读、推导与习题，再做无答案 Lab，最后独立实现小 demo。

## 学习闭环

```text
课前引导 → 理论材料 → 小习题 → Lab → 理论 Homework → 课后笔记
                                      ↓
                              独立字符级 demo → 更大项目
```

本仓库公开课程材料、题目、函数契约与公开 smoke tests。真正的核心评分器放在本地 `.grader/`（由 `.gitignore` 排除），只输出错误类别和引导，不泄露样例或答案。

## 三周课程

| 周 | 主题 | 产出 |
| --- | --- | --- |
| 1 | Q/K/V、缩放点积 attention、softmax | attention 理论题与 Lab 关卡 0–2 |
| 2 | causal mask、LayerNorm、FFN、残差与 block | 完整机制 Lab 与理论 Homework |
| 3 | 独立重写、字符级训练、生成与复盘 | 不看 Lab 答案的 mini Transformer demo |

从 [Week 1](weeks/week-01/README.md) 开始。

## 本地运行

```bash
uv sync --group dev
uv run pytest
uv run python lab/run_grade.py
```

`pytest` 只运行公开 smoke tests；`run_grade.py` 在本地存在 `.grader/` 时才执行隐藏评分。

## 项目边界

这个仓库不追求训练大模型、复刻完整论文或尽早进入 RAG。当前目标是能独立解释并实现单层、单头 Transformer 的每个机制。
