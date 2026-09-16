#!/usr/bin/env python3
"""
Export dialogue and/or audit report skeletons from state.

Agent should refine audit synthesis; this script guarantees:
- correct paths
- dialogue timeline from dialogueTurns (fallback rawData)
- audit frontmatter contract + evidence index
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline_data import OUTLINE, slug  # noqa: E402
from validate_coverage import load_state  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M")


def yaml_str(s: str | None) -> str:
    """Always JSON-encode so commas/colons/hashes cannot break YAML."""
    return json.dumps("" if s is None else str(s), ensure_ascii=False)


def yaml_list(items: list | None) -> str:
    return json.dumps([str(x) for x in (items or [])], ensure_ascii=False)


SKELETON_NOTE = (
    "_insufficient_data：export_reports.py 只保证骨架与 frontmatter。"
    "Agent 须按 `references/compile.md` 从 rawData 编译本节并写回 state 后重新导出。_"
)


def render_dialogue(state: dict) -> str:
    subject = state.get("subject", "unknown")
    mode = state.get("mode", "")
    coverage = state.get("coverage") or []
    done = sum(1 for c in coverage if c.get("status") == "done")
    total = len(coverage) or len(OUTLINE.get(mode, []))
    turns = state.get("dialogueTurns") or []
    lines = [
        f"# 对话报告 — {subject}",
        "",
        f"- 模式：{mode}",
        f"- 生成时间：{utc_now()}",
        f"- 状态文件：expression-audit/{{subject}}.state.json".replace("{subject}", _stem_subject(state)),
        f"- 话轮数：{len(turns)}",
        f"- 覆盖：{done}/{total}",
        "",
        "## 时间线",
        "",
    ]
    if turns:
        theme = (state.get("thread") or {}).get("theme") or "主线"
        lines.append(f"### 脉络：{theme}")
        lines.append("")
        for t in turns:
            role = t.get("role")
            label = "访谈者" if role == "interviewer" else "我"
            lines.append(f"**{label}：** {t.get('text', '').strip()}")
            meta = []
            if t.get("linkedQuestions"):
                meta.append("关联提纲：" + ", ".join(t["linkedQuestions"]))
            if t.get("kind"):
                meta.append(f"种类：{t['kind']}")
            if meta:
                lines.append("")
                lines.append("> " + " · ".join(meta))
            lines.append("")
    else:
        lines.append("_尚无 dialogueTurns；以下从 rawData 按题号回退（问卷感较强，建议访谈中写入 turns）。_")
        lines.append("")
        raw = state.get("rawData") or {}
        for qid in sorted(raw.keys(), key=lambda x: int(re.sub(r"\D", "", x) or 0)):
            item = raw[qid]
            if not isinstance(item, dict):
                continue
            lines.append(f"### {qid}")
            lines.append(f"**问：** {item.get('question', '')}")
            lines.append(f"**答：** {item.get('answer', '')}")
            fus = item.get("followUps") or []
            if fus:
                lines.append("**追问：**")
                for fu in fus:
                    lines.append(f"- {fu}")
            lines.append("")

    tensions = state.get("tensionLog") or []
    lines.append("## 张力时刻")
    lines.append("")
    if not tensions:
        lines.append("- （无）")
    else:
        for t in tensions:
            flag = "已解决" if t.get("resolved") else "未解决"
            lines.append(f"- [{t.get('id', '')}] ({flag}) {t.get('description', '')}")
    lines.append("")

    open_loops = (state.get("thread") or {}).get("openLoops") or []
    lines.append("## 未闭合线索")
    lines.append("")
    if not open_loops:
        lines.append("- （无）")
    else:
        for o in open_loops:
            lines.append(f"- {o}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _stem_subject(state: dict) -> str:
    return slug(state.get("subject") or "subject")


def _anchor_lines(state: dict) -> list[str]:
    pa = state.get("prototypeAnchors") or {}
    lines = []
    for key in ("anchor1", "anchor2", "anchor3"):
        item = pa.get(key) or {}
        status = item.get("status") or "pending"
        if status in ("", "pending") and not item.get("hypothesis"):
            continue
        hypo = item.get("hypothesis") or ""
        lines.append(
            f"- **{key}** status={status} hypothesis_only — {hypo or '（无类型名；仅结构摘要）'}"
        )
    return lines


def _graph_lines(state: dict) -> list[str]:
    kg = state.get("knowledgeGraph") or {}
    lp = state.get("learningPath")
    lines = []
    nodes = kg.get("nodes") if isinstance(kg, dict) else None
    if nodes:
        lines.append(f"- 图谱节点数：{len(nodes)}")
    if lp:
        lines.append("- 学习路径：已写入 state（见 learningPath）")
    return lines


def render_audit(state: dict) -> str:
    subject = state.get("subject", "unknown")
    mode = state.get("mode", "")
    coverage = state.get("coverage") or []
    done = sum(1 for c in coverage if c.get("status") == "done")
    total = len(coverage) or len(OUTLINE.get(mode, []))
    ci = state.get("coreIdentity") or {}
    qr = state.get("quickReference") or {}
    four = state.get("fourSentences") or {}
    ns = state.get("candidateNorthStar") or {}
    insufficient = list(four.get("insufficient") or [])
    if not ci.get("statement"):
        insufficient.append("identity")
    identity = ci.get("statement") or ""
    confidence = ci.get("confidence") or (
        "preliminary" if done < max(total * 0.6, 1) else "moderate" if done < total else "high"
    )
    always = qr.get("always") or []
    never = qr.get("never") or []
    moves = qr.get("signatureMoves") or []
    tensions = [t.get("description", "") for t in (state.get("tensionLog") or []) if t.get("description")]
    audience = ""
    domain = ""

    fm = [
        "---",
        "schema: expression-audit-report",
        'schema_version: "2"',
        f"subject: {yaml_str(subject)}",
        f"mode: {mode}",
        f"generated_at: {yaml_str(utc_now())}",
        f"source_state: {yaml_str('expression-audit/' + _stem_subject(state) + '.state.json')}",
        f"coverage_done: {done}",
        f"coverage_total: {total}",
        f"north_star: {yaml_str(ns.get('direction') or '')}",
        f"identity: {yaml_str(identity)}",
        f"belief: {yaml_str(four.get('belief') or '')}",
        f"vision: {yaml_str(four.get('vision') or '')}",
        f"anti_vision: {yaml_str(four.get('antiVision') or '')}",
        f"practice: {yaml_str(four.get('practice') or '')}",
        f"always: {yaml_list(always)}",
        f"never: {yaml_list(never)}",
        f"signature_moves: {yaml_list(moves)}",
        f"voice: {yaml_list([])}",
        f"taboos: {yaml_list([])}",
        f"tensions: {yaml_list(tensions[:12])}",
        f"audience: {yaml_str(audience)}",
        f"domain: {yaml_str(domain)}",
        f"confidence: {confidence}",
        f"insufficient: {yaml_list(sorted(set(insufficient)))}",
        "---",
        "",
    ]

    body = [
        f"# 审计报告 — {subject}",
        "",
        "## 0. 使用说明（Anti-Overfitting）",
        "",
        "- 结论必须能在对话报告或 rawData 中找到依据。",
        "- 不要为了文案流畅抹平 Tension Log。",
        "- `never` / 禁区是硬约束；`insufficient` 中的字段不得当事实。",
        "- 下游 Skill 读取约定见 skill 内 `references/consumer-contract.md`。",
        "- `export_reports.py` 保证路径、frontmatter、对话时间线与证据索引；"
        "§5–8 / §10–11 无编译结果时为占位，不编造。",
        "",
        "## 1. Core Identity",
        "",
        identity or "_insufficient_data_",
        "",
        f"_confidence: {confidence}_",
        "",
        "## 2. 四句话",
        "",
        f"**我相信：** {four.get('belief') or '（不足）'}",
        "",
        f"**所以我希望：** {four.get('vision') or '（不足）'}",
        "",
        f"**我绝不希望世界变成：** {four.get('antiVision') or '（不足）'}",
        "",
        f"**因此我选择：** {four.get('practice') or '（不足）'}",
        "",
        "## 3. Quick Reference",
        "",
        "### Always",
        "",
    ]
    body.extend([f"- {x}" for x in always] or ["- （空）"])
    body += ["", "### Never", ""]
    body.extend([f"- {x}" for x in never] or ["- （空）"])
    body += ["", "### Signature Moves", ""]
    body.extend([f"- {x}" for x in moves] or ["- （空）"])
    body += ["", "## 4. 北极星与定位", ""]
    if ns.get("direction"):
        body.append(f"**核心方向：** {ns['direction']}")
    else:
        body.append("_无 candidateNorthStar；可由 Agent 在访谈后补全并写回 state 再导出。_")
    body += ["", "## 5. 表达机制与声音", "", SKELETON_NOTE]
    body += ["", "## 6. 边界与禁区", ""]
    if never:
        body.extend([f"- {x}" for x in never])
        body.append("")
        body.append("_taboos 其余条目须 Agent 从 D6/D3 rawData 编译。_")
    else:
        body.append(SKELETON_NOTE)
    if mode == "quick":
        body += ["", "## 7. 内容架构与节律", "", "_quick 模式默认不写本节；升级 core 后编译。_"]
        body += ["", "## 8. 审美与辨别力", "", "_quick 仅有 Q96 时只作辨别力快照，不写完整 D3/D7 节。_"]
    else:
        body += ["", "## 7. 内容架构与节律", "", SKELETON_NOTE]
        if mode == "deep":
            body += ["", "## 8. 审美与辨别力", "", SKELETON_NOTE]
        else:
            body += ["", "## 8. 审美与辨别力", "", "_core 不含 D3/D7；升级 deep 后编译。_"]
    body += ["", "## 9. Tension Log", ""]
    tlog = state.get("tensionLog") or []
    if not tlog:
        body.append("- （无）")
    else:
        for t in tlog:
            body.append(
                f"- **{t.get('id', '')}** resolved={t.get('resolved')} — {t.get('description', '')} "
                f"(sources: {', '.join(t.get('sourceQuestions') or [])})"
            )
    body += ["", "## 10. 原型评估", ""]
    anchors = _anchor_lines(state)
    if mode == "quick":
        body.append("_quick 默认不写正式原型。无词典时禁止发明类型名。_")
    elif anchors:
        body.append("_hypothesis_only；无 `proto-system/archetypes.md` 时不得输出确认类型名。_")
        body.append("")
        body.extend(anchors)
    else:
        body.append("insufficient_dictionary")
        body.append("")
        body.append(SKELETON_NOTE)
    body += ["", "## 11. 影响图谱与学习路径", ""]
    graphs = _graph_lines(state)
    if graphs:
        body.extend(graphs)
    else:
        body.append(SKELETON_NOTE)
    body += ["", "## 12. 证据索引", "", "| ID | 模块 | 维度 | 摘要 |", "|----|------|------|------|"]
    raw = state.get("rawData") or {}
    for qid in sorted(raw.keys(), key=lambda x: int(re.sub(r"\D", "", x) or 0)):
        item = raw[qid]
        if not isinstance(item, dict):
            continue
        ans = (item.get("answer") or "").replace("\n", " ").strip()
        if len(ans) > 80:
            ans = ans[:77] + "..."
        tags = ",".join(item.get("tags") or [])
        body.append(f"| {qid} | {item.get('module', '')} | {tags} | {ans} |")
    body += [
        "",
        "## 13. 下一步",
        "",
        "- 需要更密数据：升级 mode（quick→core→deep）",
        "- 只要原话：导出 dialogue",
        "- 下游写稿/风控：只读本文件 frontmatter",
        "",
        "---",
        "",
        "_本文件可由 export_reports.py 生成骨架；Core Identity / Quick Reference / 四句话 "
        "若为空，应由访谈 Agent 编译进 state 后重新导出。_",
        "",
    ]
    return "\n".join(fm + body)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--only", choices=["dialogue", "audit", "both"], default="both")
    p.add_argument("--to", choices=["main", "exports", "both"], default="main")
    args = p.parse_args()

    ws = Path(args.workspace).expanduser().resolve()
    try:
        path, state = load_state(ws, args.subject)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 1
    root = path.parent
    (root / "exports").mkdir(exist_ok=True)
    stem = path.name.replace(".state.json", "")

    written = []
    if args.only in ("dialogue", "both"):
        text = render_dialogue(state)
        main_path = root / f"{stem}.dialogue.md"
        if args.to in ("main", "both"):
            main_path.write_text(text, encoding="utf-8")
            written.append(main_path)
        if args.to in ("exports", "both"):
            exp = root / "exports" / f"{stem}-dialogue-{stamp()}.md"
            exp.write_text(text, encoding="utf-8")
            written.append(exp)
        state.setdefault("outputs", {})
        state["outputs"]["dialoguePath"] = str(main_path)

    if args.only in ("audit", "both"):
        text = render_audit(state)
        main_path = root / f"{stem}.audit.md"
        if args.to in ("main", "both"):
            main_path.write_text(text, encoding="utf-8")
            written.append(main_path)
        if args.to in ("exports", "both"):
            exp = root / "exports" / f"{stem}-audit-{stamp()}.md"
            exp.write_text(text, encoding="utf-8")
            written.append(exp)
        state.setdefault("outputs", {})
        state["outputs"]["auditPath"] = str(main_path)

    state.setdefault("outputs", {})
    state["outputs"]["compiledAt"] = utc_now()
    state["outputs"]["modeAtCompile"] = state.get("mode")
    if state.get("metadata"):
        state["metadata"]["updatedAt"] = utc_now()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for w in written:
        print(f"OK {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
