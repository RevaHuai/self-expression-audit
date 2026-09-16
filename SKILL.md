---
name: self-expression-audit
description: >-
  自我表达审计 Skill。以访谈方式挖清表达结构：提纲必覆盖、脉络可衍生。
  交付可单独导出且可持久化的「对话报告」与「审计报告」，供人回顾与下游 Skill 消费。
  用户要求自我表达审计、表达结构访谈、写对话/审计报告、续作上次审计、导出表达档案时使用。
  不用于代写内容、人设包装或娱乐化人格测评。
---

# 自我表达审计

## 一句话

用**访谈**（不是线性问卷）挖清表达结构，产出两份可导出、可持久化、可被下游 Skill 读取的报告。

## 核心任务

1. 按模式（quick / core / deep）覆盖提纲必答题
2. 沿用户回答的**脉络衍生**追问，题号只是索引不是播放列表
3. 写回唯一真源 state
4. 编译并落盘：**对话报告** + **审计报告**（可拆开导出）
5. 支持跨会话续作；完成后可升级模式或交给下游 Skill

## 不做

- 代写内容、人设包装、娱乐化人格测评
- 替用户下道德判断或「正确人生」裁决
- 为凑覆盖打断正在出金的故事
- 一次性抛多题
- 另建与 state 平行的第二真源

## 交付物

| 交付物 | 读者 | 内容 | 默认路径 |
|--------|------|------|----------|
| **对话报告** | 被访谈者 | 按会话/脉络的问答原文、追问、张力时刻 | `{workspace}/expression-audit/{subject}.dialogue.md` |
| **审计报告** | 人 + 下游 AI/Skill | 身份、信念/愿景/反愿景、机制、禁区、张力、四句话、Quick Reference；含 frontmatter 契约 | `{workspace}/expression-audit/{subject}.audit.md` |
| **状态真源** | 本 Skill | rawData、coverage、thread、tensionLog、编译缓存 | `{workspace}/expression-audit/{subject}.state.json` |
| **导出副本**（可选） | 用户指定 | 时间戳副本 | `{workspace}/expression-audit/exports/` |

规则：

- 报告**只从 state 编译**
- 用户说「只要对话」或「只要审计」→ 只导出对应文件
- 落盘目录可由用户覆盖；未指定则用上表默认

## 运行模式与题号口径

| 模式 | 必覆盖 | 覆盖范围 | 产出密度 |
|------|--------|----------|----------|
| `quick` | **10** | 高密度精选（含 Q96 一刀辨别力） | 精简双报告 + 升级邀请 |
| `core` | **70** | D0+D1+D2+D5+D6（**不含** D3/D7） | 完整双报告（假设级锚点） |
| `deep` | **95** | core + D3 + D7 | 完整双报告（可复核锚点） |

**口径（必读）：** 有效提纲题 **95** 道；编号保留 Q1–Q108；**Q61–Q73 为空号（原 D4 已删，禁止补造）**。  
详见 [references/numbering.md](references/numbering.md)。  
题单：[references/outline.md](references/outline.md)；题面：`modules/`、`quick-mode/`。  
思想来源：[references/intellectual-sources.md](references/intellectual-sources.md)。

**原型说明：** `proto-system/` 只有假设→验证**流程**，**无**十二型词典入库。锚点输出必须标 `hypothesis_only`，禁止假装「已确认人格类型」。

## 启动与状态判断

每轮会话开始时：

```text
1. 扫描 {workspace}/expression-audit/*.state.json
2. 若用户点名 subject → 打开对应 state
3. 否则：
   - 有未完成 → 询问续作 / 换人 / 新开
   - 全部完成 → 询问导出 / 升级 / 新开 / 给下游用
   - 无文件 → 询问 subject 名称 + 模式
4. 用户只要导出/编译 → 跳过访谈，直接 compile
```

初始化可用：

```bash
python3 scripts/init_state.py --workspace "{workspace}" --subject "{name}" --mode core
```

## 主循环（每轮只做一步）

详细决策见 [references/interview-engine.md](references/interview-engine.md)。

```text
读 state
  → 用户意图是导出/升级/停？按动作处理并结束本轮关键步骤
  → 否则选「此刻唯一一刀」：
        if 高价值线索未挖完 → 沿 thread 衍生追问
        else if 未闭合张力可温和照亮 → 张力一问
        else if coverage 有未覆盖 → 选与当前脉络最近的必答题
        else → 收敛四句话 → 编译双报告 → 落盘 → 询问导出/升级
  → 写回 state（原文、coverage、thread、tension、dialogueTurns）
  → 一次只抛一个问题或一个确认，然后停
```

### 硬规则

1. **一次一个问题**（或一条张力照亮）；不要清单式连问
2. **题号不进用户可见话术**（除非用户追问进度）；内部用 Q 编号索引
3. **提纲必覆盖**：衍生再多，模式结束前 coverage 必须全部 done
4. **记录原文**：模块进行中不做长总结；总结只在编译时
5. **张力照亮不求解决**：记入 tensionLog 即可
6. **不提供选项、不代填答案**
7. **Anti-overfitting**：Core Identity / Quick Reference 必须有具体回答作证据；张力优先于整洁结论

## 双报告编译

触发：模式 coverage 完成、用户说「先出报告」、升级前快照、用户只要导出。

流程与模板：[references/compile.md](references/compile.md)  
（`compiler/compile.md` 保留为兼容入口，指向同一套规则。）

```bash
python3 scripts/export_reports.py --workspace "{workspace}" --subject "{name}" [--only dialogue|audit] [--to exports]
```

覆盖率检查：

```bash
python3 scripts/validate_coverage.py --workspace "{workspace}" --subject "{name}"
```

## 下游消费

审计报告 frontmatter + 正文结构是其他 Skill 的输入契约。  
见 [references/consumer-contract.md](references/consumer-contract.md)。

示例方向（本 Skill 不实现）：按 voice/never 改稿、按 taboos/tensions 做发布前表达检查、按 north_star 做选题。

## 愿景 / 反愿景（收敛物）

D1 挖愿景，D6 挖反愿景。审计结束必须尽量收敛为四句话（信息不足则标明缺口）：

> **我相信：______。**  
> **所以我希望：______。**  
> **我绝不希望世界变成：______。**  
> **因此我选择：______。**

## 模块与文件索引

| 路径 | 用途 |
|------|------|
| `references/numbering.md` | 95/空号/模式口径真源 |
| `references/outline.md` | 模式 × 必覆盖题号提纲 |
| `references/interview-engine.md` | 选下一问 / 衍生 / 张力 / 覆盖策略 |
| `references/compile.md` | 双报告编译 |
| `references/consumer-contract.md` | 下游读取契约 |
| `references/intellectual-sources.md` | 思想来源与设计原则 |
| `modules/D*.md` | 各板块题面与追问规则（题库） |
| `modules/north-star-exploration.md` | D0 完成后的可选分析引擎（不问新题） |
| `quick-mode/questions.md` | quick 十题精选与简化追问 |
| `proto-system/prototype-anchors.md` | 三阶原型锚点 |
| `schemas/state.schema.json` | 状态 schema（亦兼容根目录 `state-schema.json`） |
| `scripts/*` | 初始化 / 导出 / 覆盖率 / 自更新 |

## 北极星深度探索（可选）

用户说「深度探索北极星」等且**当前模式的 D0 coverage 已完成**时：读 state，跑 `modules/north-star-exploration.md` 分析引擎，**不问新题**；结果写回 state 并可选并入审计报告。quick 的 D0 只有 3 题，分析必须标 `preliminary`，不得按 18 题分母拒绝。

## 升级

- **保留** rawData 与 dialogue；审计报告按新模式重编译
- **quick→core：** coverage **重建为 core 70**；已答 quick 题标 done；**Q96 留在 rawData，但不进 core coverage**（core 不含 D7）
- **core→deep / quick→deep：** coverage = deep 95；已有 Q96 则 done，可「深化追问」写入 followUps
- 同模式重开：新 subject 或 archive，禁止静默清空
- 上一模式 coverage 未完成也可升级（脚本警告）；`completedModes` **仅在**上一模式全 done 时写入
- 脚本：`scripts/outline_data.rebuild_coverage_for_upgrade`；CLI：`scripts/upgrade_mode.py`

## 停止条件

| 情况 | 动作 |
|------|------|
| 本轮已提出一个问题/追问 | 停止，等用户 |
| 用户明确暂停 | 保存 state，告知路径 |
| coverage 完成且报告已落盘 | 停止；给导出与升级选项 |
| 用户只要导出 | 编译后停止 |
| 信息不足无法诚实编译某字段 | 字段标 `insufficient_data`，不编造 |

## 兼容说明

- 旧路径 `{workspace}/.claude/skills/self-expression-audit/state/` 若存在可读入并迁移到 `expression-audit/`
- 根目录 `state-schema.json` 与 `schemas/state.schema.json` 保持同步；以 schemas 为准
- 题库 modules 文案本轮不重写；改变的是**调度语义**（提纲覆盖 + 访谈脉络）
- 更新 skill 用 `bash scripts/update.sh`（可加 `--yes`）。**不会改 origin**；工作区脏则拒绝。
