# 提纲：模式 × 必覆盖点

题号是**覆盖索引**，不是播放顺序。  
调度见 [interview-engine.md](interview-engine.md)。  
**口径真源**见 [numbering.md](numbering.md)（有效 **95** 题；Q61–Q73 空号；quick 10 / core 70 / deep 95）。

完整题面：`modules/`、`quick-mode/questions.md`。  
思想来源：[intellectual-sources.md](intellectual-sources.md)。

## 模块地图

| 模块 | 文件 | 题号 | 题量 | 挖什么 |
|------|------|------|------|--------|
| D0 | `modules/D0-polaris.md` | Q1–Q18 | 18 | 北极星、领域、身份 |
| D1 | `modules/D1-beliefs.md` | Q19–Q33 | 15 | 信念、反共识、愿景 |
| D2 | `modules/D2-mechanism.md` | Q34–Q48 | 15 | 表达机制与声音 |
| D3 | `modules/D3-aesthetics.md` | Q49–Q60 | 12 | 审美禁区（仅 deep） |
| — | （无文件） | **Q61–Q73** | **0** | **空号；禁止补造** |
| D5 | `modules/D5-architecture.md` | Q74–Q85 | 12 | 内容架构与节律 |
| D6 | `modules/D6-taboo.md` | Q86–Q95 | 10 | 绝对禁区、反愿景 |
| D7 | `modules/D7-danger-signals.md` | Q96–Q108 | 13 | 危险信号（deep；quick 仅 Q96） |

**有效合计 95。** 无 D4 模块。

## 依赖（软约束）

```text
D0 建议先完成（建立坐标系）
D1 / D2 / D5 / D6 依赖 D0 语境
D6 宜在身份与信任建立后（勿与 D0 抢跑）
D3 / D7 主要在 deep；若脉络强相关可穿插题面，但 coverage 仍按模式
```

D0 未完成时：pending **优先 D0**，除非用户明确要求先谈某主题（记 meta，仍回到 D0 缺口）。

## quick（10）

| tie-break 序 | ID | 模块 | 题眼 |
|--------------|-----|------|------|
| 1 | Q1 | D0 | 最触动的表达者/思想家 |
| 2 | Q13 | D0 | 完整定位陈述 |
| 3 | Q18 | D0 | Ikigai 交叉 |
| 4 | Q19 | D1 | 反共识 |
| 5 | Q33 | D1 | 最大主张 |
| 6 | Q34 | D2 | 向朋友介绍 |
| 7 | Q38 | D2 | 自然 gravitate 的形式 |
| 8 | Q86 | D6 | 绝对不碰的表达 |
| 9 | Q88 | D6 | 「我永远不会那样」 |
| 10 | Q96 | D7 | 不信任信号（**仅此一道 D7**） |

说明：quick **故意**含 Q96；core **不含**整板 D7。见 [numbering.md](numbering.md)。

## core（70）

- D0: Q1–Q18（18）  
- D1: Q19–Q33（15）  
- D2: Q34–Q48（15）  
- D5: Q74–Q85（12）  
- D6: Q86–Q95（10）  

**合计 70。不含 D3、不含 D7。**  
模块推进暗示（仅 tie-break）：D0 → D1 → D2 → D5 → D6。

## deep（95）

core 全部 + D3 Q49–Q60（12）+ D7 Q96–Q108（13）= **95**。

## 升级时的 coverage 规则

| 从 → 到 | coverage 怎么建 | rawData / 对话 |
|---------|-----------------|----------------|
| quick → core | **新清单 = core 70**；已答的 Q1/13/18/19/33/34/38/86/88 标 done；**Q96 不进入 core coverage**，但 rawData 与 dialogue **保留** | 不删 Q96 |
| quick → deep | 清单 = deep 95；已答含 Q96 则 done；可深化 followUps | 保留全部 |
| core → deep | 清单 = deep 95；补 D3 全部 + D7 全部；若历史 rawData 已有 Q96（曾做 quick）则 Q96 done | 保留 |
| 同模式重开 | 新 subject 或 archive 旧 state；**禁止静默清空** | — |

升级话术：对已答且需加深的题，用「深化追问」，不否定原答。

实现：`scripts/outline_data.py` → `rebuild_coverage_for_mode(state, new_mode)`。

## 初始化 coverage 伪代码

```text
ids = OUTLINE[mode]
state.coverage = [
  { id, module, status: rawData[id].answer ? "done" : "pending", depth: mode, via: "outline" }
  for id in ids
]
# 绝不把 Q61–Q73 写入 coverage
```

## 进度聚合

```text
progress 只含 D0,D1,D2,D3,D5,D6,D7
progress[module].status = complete | partial | not_started
按该模式 coverage 中属于该 module 的子集统计
```
