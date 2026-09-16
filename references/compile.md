# 双报告编译

**真源：** `{workspace}/expression-audit/{subject}.state.json`  
**产出：**

- `{subject}.dialogue.md` — 对话报告  
- `{subject}.audit.md` — 审计报告（含 YAML frontmatter 契约）

兼容：旧版单文件报告逻辑见下文「字段映射」；不再默认输出混合的 `*-core.md` 单卷（用户点名时可另存 exports）。

## 触发

1. 当前模式 coverage 全部 done  
2. 用户「先出报告 / 导出 / 只要对话 / 只要审计」  
3. 升级前快照  
4. `scripts/export_reports.py`

## 编译前整理（只写回 state，再渲染）

1. **维度标签**：为 rawData 各答标注 identity / belief / aesthetic / fear / mechanism / audience / contradiction / aspiration / discernment（可多选）  
2. **Core Identity**：2–3 句，必须能指回具体回答；&lt;5 题有效身份信号 → `confidence: preliminary`  
3. **Quick Reference**：always ≤5 / never ≤5 / signatureMoves ≤3；每条尽量 ≥2 题证据，不足则减条不编造  
4. **四句话**：Belief / Vision / Anti-Vision / Practice；缺口标 `insufficient_data`  
5. **Tension Log**：完整保留；已自然化解的标 resolved  
6. **原型锚点**：按 `proto-system/prototype-anchors.md`；无词典时写 `insufficient_dictionary` / hypothesis_only，禁止虚构类型名；quick 默认不写正式原型  
7. **北极星 / 图谱**：若 state 中有 candidateNorthStar / knowledgeGraph / northStarExploration 则并入审计报告对应节  

Anti-overfitting：禁止套模板句；张力优先于整洁。

---

## A. 对话报告 `{subject}.dialogue.md`

### 目的

给**被访谈者本人**回顾：像读访谈录，不像读测评。

### 结构

```markdown
# 对话报告 — {subject}

- 模式：quick|core|deep
- 生成时间：...
- 状态文件：expression-audit/{subject}.state.json
- 话轮数：N
- 覆盖：done/total

## 时间线

### 会话片段 / 脉络：{theme}

**访谈者：** ...
**我：** ...

> 关联提纲：Q19（仅脚注式，可折叠在斜体行）
> 种类：outline | probe | tension

...

## 张力时刻

- [回合] 摘要：...

## 未闭合线索（若有）

- ...

## 附录：按题号索引（可选）

| ID | 模块 | 回答摘要（首行） |
```

### 规则

- **主路径按 dialogueTurns 顺序**，不要按 Q1→Q108 重排主文  
- 题号只作脚注/附录，避免问卷感  
- 原文不改写；最多做极轻的换行整理  
- 可单独导出：用户只要对话时**不强制**生成审计报告（若 audit 已过期可提示「审计未刷新」）

---

## B. 审计报告 `{subject}.audit.md`

### 目的

给人扫结论 + 给**下游 Skill** 当语境底座。

### Frontmatter（契约，必须）

```yaml
---
schema: expression-audit-report
schema_version: "2"
subject: "{subject}"
mode: quick|core|deep
generated_at: "{ISO-8601}"
source_state: "expression-audit/{subject}.state.json"
coverage_done: 70
coverage_total: 70
north_star: "..."          # 可空字符串
identity: "..."            # Core Identity 短句
belief: "..."
vision: "..."
anti_vision: "..."
practice: "..."
always: []
never: []
signature_moves: []
voice: []                  # 表达机制关键词
taboos: []
tensions: []               # 短摘要列表
audience: "..."
domain: "..."
confidence: preliminary|moderate|high
insufficient: []           # 字段名列表
---
```

字段语义见 [consumer-contract.md](consumer-contract.md)。

### 正文结构

```markdown
# 审计报告 — {subject}

## 0. 使用说明（Anti-Overfitting）
- 如何用 / 如何不用这份文档
- 张力不要被下游抹平

## 1. Core Identity
...

## 2. 四句话
我相信 / 所以我希望 / 我绝不希望 / 因此我选择

## 3. Quick Reference
### Always
### Never
### Signature Moves

## 4. 北极星与定位
（卡片：方向、吸引源、反复属性、不想成为、证据、未来投射）
（有数据才写；无则省略或标不足）

## 5. 表达机制与声音
...

## 6. 边界与禁区
...

## 7. 内容架构与节律（core/deep）
...

## 8. 审美与辨别力（deep：D3/D7）
...

## 9. Tension Log
完整条目

## 10. 原型评估（若有锚点）
...

## 11. 影响图谱与学习路径（若有）
...

## 12. 证据索引
题号 → 维度标签 → 一句话锚点（**不是**全文问答；全文在对话报告）

## 13. 下一步
升级 / 导出 / 下游建议
```

### 模式差异

| 部分 | quick | core | deep |
|------|-------|------|------|
| Core Identity | 必标初步 | 综合 | 更密 |
| Quick Reference | 1–2 条量级 | 完整 | 可含 D3/D7 |
| 原型 | 默认无 | 初步 | 复核 |
| 图谱/学习路径 | 信号级 | 摘要 | 完整 |
| 升级邀请 | 要 | 可有 | 无 |

### 与对话报告的分工

| | 对话报告 | 审计报告 |
|--|----------|----------|
| 原文问答 | 主文 | 仅证据索引 |
| 结构结论 | 少 | 主文 |
| frontmatter 契约 | 无（或仅 meta） | **必须** |
| 下游 Skill | 一般不读 | **主输入** |

---

## 渲染规则

1. 只使用 state 中已有信息；禁止用「一般创作者都…」补全  
2. `insufficient` 中的字段正文写明「信息不足」  
3. UTF-8 Markdown；frontmatter 用 YAML（字符串与列表一律 JSON 编码，避免逗号拆项）  
4. 落盘后更新 state：`outputs.dialoguePath` / `outputs.auditPath` / `outputs.compiledAt`  
5. `--only dialogue|audit` 时只写对应文件，仍可读完整 state  
6. **`scripts/export_reports.py` 是骨架导出器**：保证路径、frontmatter 契约、对话时间线、Tension Log、证据索引。§5–8 / §10–11 在 state 无编译结果时写 `insufficient_data` 占位，**不编造**。终稿仍须 Agent 按本节把综合写入 state 再导出。  

## 导出副本

```text
expression-audit/exports/{subject}-{dialogue|audit}-{YYYYMMDD-HHMM}.md
```

不覆盖主文件，便于版本回顾。

## 旧路径迁移

若发现：

```text
{workspace}/.claude/skills/self-expression-audit/state/*-state.json
{workspace}/.claude/skills/self-expression-audit/output/*
```

编译前可复制/迁移到 `expression-audit/`，并在 dialogue 元信息注明 migrated_from。
