# 下游消费契约

其他 Skill / Agent **只读审计报告**即可工作；不要解析访谈过程，不要改 state（除非用户明确授权「回写审计」）。

## 输入优先级

1. `{workspace}/expression-audit/{subject}.audit.md` 的 YAML frontmatter  
2. 同文件正文对应章节（frontmatter 空时回退）  
3. 仅当用户要求「对照原话」时再打开 `{subject}.dialogue.md`  
4. **不要**把 `.state.json` 当对外 API（字段比报告更易变）

## Frontmatter 字段

| 字段 | 类型 | 下游用途 |
|------|------|----------|
| `schema` | string | 固定 `expression-audit-report` |
| `schema_version` | string | 当前 `"2"`；不兼容时递增 |
| `subject` | string | 档案人 |
| `mode` | enum | 数据密度预期 |
| `confidence` | enum | 是否敢强约束生成 |
| `north_star` | string | 选题、定位、长期方向 |
| `identity` | string | 人设底色（非营销口号） |
| `belief` / `vision` / `anti_vision` / `practice` | string | 四句话操作系统 |
| `always` | string[] | 必须保留的表达行为 |
| `never` | string[] | 硬禁止 |
| `signature_moves` | string[] | 可强化的手法 |
| `voice` | string[] | 语气/形式关键词 |
| `taboos` | string[] | 题材与姿态禁区 |
| `tensions` | string[] | 生成时保留张力，勿强行统一 |
| `audience` / `domain` | string | 读者与领域 |
| `insufficient` | string[] | 这些键不可当事实用 |

## 合规使用

**应该：**

- 写稿/改稿时把 `never` + `taboos` 当硬过滤  
- 需要立场时用四句话，而不是发明新价值观  
- 遇到 `tensions` 在文中保留复杂度，或显式提问用户  
- `confidence: preliminary` 或 `insufficient` 非空时降低断言强度  

**不应该：**

- 把审计报告当「用户已授权发布」的内容本身  
- 用报告冒充专业心理/医疗诊断  
- 为了文案流畅抹掉 never/taboos  
- 在用户未指定 subject 时擅自合并多人档案  

## 最小读取示例（伪代码）

```text
doc = read_markdown(audit_path)
meta = parse_yaml_frontmatter(doc)
assert meta.schema == "expression-audit-report"
for rule in meta.never + meta.taboos:
    reject_or_rewrite_if_violates(draft, rule)
apply_voice(meta.voice, meta.signature_moves)
ground_claims(meta.belief, meta.vision, meta.practice)
```

## 建议的下游 Skill 方向（不在本包实现）

| 方向 | 主要消费字段 |
|------|----------------|
| 表达对齐改稿 | voice, always, never, signature_moves |
| 发布前表达风险 | taboos, never, tensions, anti_vision |
| 选题/定位 | north_star, audience, domain, vision |
| 人设一致性检查 | identity, four sentences, tensions |

## 版本

- `schema_version: "2"`：双报告拆分后的契约（本重构）  
- 若增加必填字段：版本 +1，并在本文件写迁移说明  
