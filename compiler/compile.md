---
title: 产出文档编译系统（兼容入口）
description: v2 起双报告规则以 references/compile.md 为准。本文件保留路径兼容。
---

# 产出文档编译系统

> **Canonical spec:** [../references/compile.md](../references/compile.md)  
> **Consumer contract:** [../references/consumer-contract.md](../references/consumer-contract.md)  
> **Interview scheduling:** [../references/interview-engine.md](../references/interview-engine.md)

## v2 变更摘要

| 旧（v1） | 新（v2） |
|----------|----------|
| 单卷模式报告 `*-quick/core/deep.md` | **对话报告** + **审计报告** 拆分 |
| 输出在 skill 目录 `output/` | `{workspace}/expression-audit/` |
| 线性题序编译附录 | 对话报告按 `dialogueTurns` 脉络；审计报告只留证据索引 |
| 无稳定下游 API | 审计报告 YAML frontmatter `schema: expression-audit-report` |

Agent 与脚本应实现 **references/compile.md**，不要只读本文件的旧模板。

## 快速调用

```bash
python3 scripts/export_reports.py \
  --workspace "{workspace}" \
  --subject "{name}" \
  --only both \
  --to main
```

只要对话或只要审计：`--only dialogue` / `--only audit`。  
时间戳副本：`--to exports` 或 `--to both`。

## 旧模板

v1 快速/核心/深度单卷模板已归档在 git 历史与  
`../backups/`（若本地做过备份）。需要对照时从备份读取，不再作为默认行为。
