"""Shared outline IDs for init/validate/export scripts.

Canonical counts: quick=10, core=70, deep=95 effective questions.
Q61–Q73 are intentional voids (deleted D4). See references/numbering.md.
"""

from __future__ import annotations

import re
from copy import deepcopy

MODULE_OF: dict[str, str] = {}
VOID_IDS = [f"Q{n}" for n in range(61, 74)]  # Q61–Q73 inclusive


def slug(subject: str) -> str:
    """Filename stem for a subject. Shared by init and load_state."""
    s = subject.strip()
    s = re.sub(r"[^\w一-鿿\-]+", "-", s, flags=re.UNICODE)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "subject"


def _range(prefix_start: int, prefix_end: int, module: str) -> None:
    for n in range(prefix_start, prefix_end + 1):
        MODULE_OF[f"Q{n}"] = module


_range(1, 18, "D0")
_range(19, 33, "D1")
_range(34, 48, "D2")
_range(49, 60, "D3")
_range(74, 85, "D5")
_range(86, 95, "D6")
_range(96, 108, "D7")

EFFECTIVE_COUNT = len(MODULE_OF)  # 95

OUTLINE = {
    "quick": [
        "Q1",
        "Q13",
        "Q18",
        "Q19",
        "Q33",
        "Q34",
        "Q38",
        "Q86",
        "Q88",
        "Q96",
    ],
    "core": (
        [f"Q{n}" for n in range(1, 19)]
        + [f"Q{n}" for n in range(19, 34)]
        + [f"Q{n}" for n in range(34, 49)]
        + [f"Q{n}" for n in range(74, 86)]
        + [f"Q{n}" for n in range(86, 96)]
    ),
    "deep": (
        [f"Q{n}" for n in range(1, 19)]
        + [f"Q{n}" for n in range(19, 34)]
        + [f"Q{n}" for n in range(34, 49)]
        + [f"Q{n}" for n in range(49, 61)]
        + [f"Q{n}" for n in range(74, 86)]
        + [f"Q{n}" for n in range(86, 96)]
        + [f"Q{n}" for n in range(96, 109)]
    ),
}

assert EFFECTIVE_COUNT == 95
assert len(OUTLINE["quick"]) == 10
assert len(OUTLINE["core"]) == 70
assert len(OUTLINE["deep"]) == 95
assert "Q96" in OUTLINE["quick"] and "Q96" not in OUTLINE["core"]
assert "Q96" in OUTLINE["deep"]
assert not any(v in OUTLINE["deep"] for v in VOID_IDS)


def module_of(qid: str) -> str:
    if qid in VOID_IDS:
        raise KeyError(f"void question id (deleted D4): {qid}")
    if qid not in MODULE_OF:
        raise KeyError(f"unknown question id: {qid}")
    return MODULE_OF[qid]


def is_void(qid: str) -> bool:
    return qid in VOID_IDS


def build_coverage(mode: str, raw_data: dict | None = None) -> list[dict]:
    """Build coverage list for a mode; mark done when rawData has non-empty answer."""
    raw_data = raw_data or {}
    items = []
    for qid in OUTLINE[mode]:
        answered = bool(
            isinstance(raw_data.get(qid), dict)
            and str(raw_data[qid].get("answer") or "").strip()
        )
        items.append(
            {
                "id": qid,
                "module": module_of(qid),
                "status": "done" if answered else "pending",
                "depth": mode,
                "answeredAt": None,
                "via": "outline",
            }
        )
    return items


def aggregate_progress(coverage: list[dict]) -> dict:
    by_mod: dict[str, list] = {}
    for c in coverage:
        by_mod.setdefault(c["module"], []).append(c)
    progress = {}
    for mod, items in by_mod.items():
        answered = [i["id"] for i in items if i["status"] == "done"]
        total = len(items)
        if not answered:
            status = "not_started"
        elif len(answered) >= total:
            status = "complete"
        else:
            status = "partial"
        progress[mod] = {
            "status": status,
            "totalQuestions": total,
            "answeredQuestions": answered,
            "availableQuestions": [i["id"] for i in items],
        }
    return progress


def rebuild_coverage_for_upgrade(state: dict, new_mode: str) -> dict:
    """
    Return a shallow-copied state with mode/coverage/progress updated for upgrade.

    Rules (numbering.md):
    - rawData and dialogueTurns preserved entirely
    - coverage rebuilt from OUTLINE[new_mode]
    - answers already in rawData → done (including Q96 when entering deep)
    - quick→core: Q96 drops out of coverage but stays in rawData
    """
    if new_mode not in OUTLINE:
        raise ValueError(f"unknown mode: {new_mode}")
    out = deepcopy(state)
    raw = out.get("rawData") or {}
    # strip any illegal void keys if present
    for v in VOID_IDS:
        raw.pop(v, None)
    out["rawData"] = raw
    prev = out.get("mode")
    completed = list(out.get("completedModes") or [])
    if prev and prev not in completed:
        # only mark completed if previous coverage was fully done
        old_cov = out.get("coverage") or []
        if old_cov and all(c.get("status") == "done" for c in old_cov):
            completed.append(prev)
    out["completedModes"] = completed
    out["mode"] = new_mode
    out["coverage"] = build_coverage(new_mode, raw)
    out["progress"] = aggregate_progress(out["coverage"])
    meta = out.setdefault("metadata", {})
    notes = meta.get("notes") or ""
    meta["notes"] = (notes + f"\n[upgrade] {prev} → {new_mode}").strip()
    return out
