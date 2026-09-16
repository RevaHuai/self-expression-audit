# 访谈引擎

问卷题库是**提纲**，不是播放列表。Agent 每轮只选「此刻最该问的那一刀」。  
题量口径：有效 **95** 题（见 [numbering.md](numbering.md)）；**不要**说「108 道都要答」。  
模块 `.md` 里的「逐题」细则只描述**该题追问**，不授权按题号线性播放。

## 状态里的两张表

### 1. coverage[]

模式开始时，按 [outline.md](outline.md) 生成必覆盖清单：

```json
{
  "id": "Q13",
  "module": "D0",
  "status": "pending | in_progress | done | deferred",
  "depth": "quick | core | deep",
  "answeredAt": null,
  "via": "outline | derived_credit"
}
```

- `done`：已有可接受原文答案（可含 followUps）
- `derived_credit`：衍生对话已实质覆盖该提纲点，编译时仍写入对应 Q 的 rawData 摘要，并在 dialogue 中保留原话轮
- 结束模式前：所有 coverage 必须 `done`（或用户显式放弃并记录 gap）

### 2. thread

当前访谈脉络：

```json
{
  "theme": "一句话主题",
  "openLoops": ["未挖完的线索"],
  "lastQuestionId": "Q19",
  "lastUserSignal": "反共识 / 故事 / 情绪峰 / 自我纠正 ...",
  "priority": "high | normal"
}
```

### 3. dialogueTurns[]

有序列：每轮用户可见交互追加一条，供对话报告使用。

```json
{
  "turn": 12,
  "ts": "ISO-8601",
  "role": "interviewer | subject",
  "text": "原文",
  "linkedQuestions": ["Q19"],
  "kind": "outline | probe | tension | meta | close"
}
```

## 每轮决策树

```text
用户消息到达
    │
    ├─ 元请求（导出/暂停/升级/换模式/只要某报告）
    │     → 执行动作，不新开提纲题
    │
    ├─ 自我纠正 / 「刚才说的不完全对」
    │     → 最高优先：停下追修正，更新 rawData + tension 若涉及
    │
    ├─ 回答含高价值信号（具体故事、命名信念、身体反应、禁区、未来意象）
    │     → 沿信号追 1 刀（kind=probe），更新 thread.openLoops
    │     → 若追问已覆盖某 coverage 点，标记 derived_credit / done
    │
    ├─ 与既有答案冲突且尚未照亮
    │     → 温和张力一问（kind=tension），写入 tensionLog
    │     → 不要求用户「解决」
    │
    ├─ coverage 仍有 pending
    │     → 在 pending 中选「与 thread.theme / openLoops 语义最近」的一题
    │     → 若无脉络，按模块依赖：D0 未完成则优先 D0 缺口；
    │       D0 完成后可在 D1/D2/D5/D6（及 deep 的 D3/D7）间按邻近度选
    │     → 用自然语言问出题面，不说「下一题是 Qxx」
    │
    └─ coverage 全 done
          → 收敛四句话（缺则标缺口）
          → 编译双报告并落盘
```

## 选「下一提纲题」的邻近度

优先级从高到低：

1. 同一 module 内未完成题
2. 与 openLoops 关键词/实体重叠的题（题面或该模块说明中的维度）
3. 愿景/反愿景成对：刚做完 D1 愿景向 → 优先 D6 相关缺口（或相反）
4. outline 默认推荐序（见 outline.md），**仅作 tie-break**

## 衍生追问（probe）规范

允许：

- 要具体时刻、原文、名字、身体感觉
- 剥离引用：「那是 TA 的话，你的呢？」
- 压缩：「一句话只留一个核心动作」
- 对照：与 thread 中另一线索轻轻对照（非质问）

禁止：

- 一次堆 2+ 个问题
- 选择题 /「你是不是想说…」代填
- 为了赶 coverage 打断用户正在展开的故事（等自然落点再收）

## 张力（tension）

记录格式与 `tensionLog` schema 一致。话术模板：

```text
你前面提到「…」，刚才又说「…」。
这两处好像有点 tension——你怎么看？
（不用圆上，聊聊就好。）
```

## 与模块文件的关系

- 题面、维度、模块内追问规则：读 `modules/D*.md` / `quick-mode/questions.md`
- 本文件只负责**调度**；不复制 95 道有效题全文
- quick：coverage 10 题（含 Q96）；probe 更克制（每题默认 0–1 次深度追问）
- core：70 题，**无** D3/D7；若 rawData 有 Q96（来自 quick），当史料保留，不当 core 缺口
- deep：95 题；已有答案可深化而非重问
- 空号 Q61–Q73：永不选入下一问
- core/deep：允许在高信号处多轮 probe，但单轮仍只一问

## 进度对用户的说法

- 默认：「我们顺着刚才的线再挖一点」/「还有一块边界想听你说」
- 用户问还要多久：给「大约还剩 N 个必经点 + 当前这条线」而不是题号列表
- 用户要求看清单：可展示 outline 未完成模块名（仍尽量少秀 Q 号）

## 写回时机

每个 subject 话轮结束后立即写 state：

1. `dialogueTurns` 追加 interviewer + subject
2. 若锚定某 Q → 更新 `rawData[Qn]`
3. 更新对应 `coverage`
4. 更新 `thread`
5. 若有张力 → `tensionLog`
6. 更新 `progress` 模块级汇总（由 coverage 聚合）

## 会话结束话术（coverage 完成时）

1. 简短致谢（不总结人格）
2. 告知已写入的三个路径：state / dialogue / audit
3. 提供选项：只要某一份、复制到 exports、升级模式、给下游 Skill 用
