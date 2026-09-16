# 自我表达审计

用**访谈**挖清表达结构：提纲必覆盖，脉络可衍生。  
交付可拆分导出、可持久化的 **对话报告** 与 **审计报告**。

**你即你的表达。** 这是自我发现工具，不是品牌包装器，也不做人格测评。

仓库：https://github.com/RevaHuai/self-expression-audit

---

## 口径

| 概念 | 值 |
|------|-----|
| 有效提纲 | **95** 题（编号 Q1–Q108；**Q61–Q73 空号**，原 D4 已删） |
| quick | 10（含 Q96） |
| core | 70（D0+D1+D2+D5+D6，不含 D3/D7） |
| deep | 95（core + D3 + D7） |

提纲是覆盖清单，不是播放列表。真源：[`references/numbering.md`](references/numbering.md)。

---

## 安装

把本仓库放到 Agent 的 Skill 目录即可，例如：

```bash
git clone https://github.com/RevaHuai/self-expression-audit.git
```

访谈数据写在**工作区** `{workspace}/expression-audit/`，不进本仓库。

---

## 对 Agent 说

```text
使用自我表达审计，核心模式，subject 叫 Alice
继续我的自我表达审计
先出报告 / 只要对话报告 / 只要审计报告
升级到深度模式
导出到 exports
```

脚本（可选）：

```bash
python3 scripts/init_state.py --workspace "$PWD" --subject Alice --mode core
python3 scripts/validate_coverage.py --workspace "$PWD" --subject Alice
python3 scripts/export_reports.py --workspace "$PWD" --subject Alice --only both
python3 scripts/upgrade_mode.py --workspace "$PWD" --subject Alice --to deep
```

---

## 落盘

```text
{workspace}/expression-audit/
├── {subject}.state.json     # 唯一真源
├── {subject}.dialogue.md    # 对话报告（给人回顾）
├── {subject}.audit.md       # 审计报告（人 + 下游 Skill）
└── exports/                 # 可选时间戳副本
```

下游只读 audit 的 YAML frontmatter（`schema: expression-audit-report`）。  
字段见 [`references/consumer-contract.md`](references/consumer-contract.md)。

---

## 仓库结构

```text
.
├── SKILL.md                 # Agent 入口：循环、硬规则、停止条件
├── README.md
├── references/              # 口径、调度、编译、下游契约
├── modules/                 # 题面（D0–D3, D5–D7）
├── quick-mode/              # quick 十题
├── proto-system/            # 锚点流程（无十二型词典）
├── schemas/state.schema.json
├── state-schema.json        # 根目录兼容副本
├── scripts/                 # init / validate / export / upgrade / update
├── evals/                   # 行为契约样本（不是 Level 3 通过证明）
└── compiler/compile.md      # 兼容入口 → references/compile.md
```

---

## 更新

```bash
bash scripts/update.sh          # 交互确认
bash scripts/update.sh --yes    # 非交互；工作区必须干净
```

- 不改写 `git remote origin`
- 有未提交改动会拒绝
- 不会清理 `expression-audit/` 里的访谈数据

---

## 版本

- **v2.1**：95 题口径 / 空号 Q61–Q73；schema 2.1；双报告与安全更新脚本
- **v2**：访谈引擎 + workspace 落盘 + 下游契约
- 题库文案沿用 v1，调度语义升级
