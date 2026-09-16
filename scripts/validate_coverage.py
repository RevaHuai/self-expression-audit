#!/usr/bin/env python3
"""Validate coverage checklist against mode outline and rawData."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline_data import OUTLINE, VOID_IDS, is_void, module_of, slug  # noqa: E402


def load_state(workspace: Path, subject: str) -> tuple[Path, dict]:
    """Resolve state file by exact stem, slug, or state.subject equality.

    Never prefix-match filenames (Al must not open Alice.state.json).
    Multiple distinct hits raise ValueError.
    """
    root = workspace / "expression-audit"
    candidates = list(root.glob("*.state.json"))
    if not candidates:
        raise FileNotFoundError(f"no state under {root}")

    hits: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.resolve()
        if path.exists() and resolved not in seen:
            hits.append(path)
            seen.add(resolved)

    add(root / f"{subject}.state.json")
    stemmed = slug(subject)
    if stemmed != subject:
        add(root / f"{stemmed}.state.json")

    # Path.stem of "Alice.state.json" is "Alice.state"
    subject_matches: list[Path] = []
    for c in candidates:
        file_stem = c.name[: -len(".state.json")] if c.name.endswith(".state.json") else c.stem
        if file_stem == subject or file_stem == stemmed:
            add(c)
            continue
        data = json.loads(c.read_text(encoding="utf-8"))
        if data.get("subject") == subject:
            subject_matches.append(c)

    if not hits and len(subject_matches) == 1:
        add(subject_matches[0])
    elif not hits and len(subject_matches) > 1:
        names = ", ".join(p.name for p in subject_matches)
        raise ValueError(f"ambiguous subject={subject!r}: {names}")

    if not hits:
        raise FileNotFoundError(f"state not found for subject={subject!r} in {root}")
    if len(hits) > 1:
        names = ", ".join(p.name for p in hits)
        raise ValueError(f"ambiguous subject={subject!r}: {names}")

    path = hits[0]
    return path, json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--strict-raw", action="store_true", help="require rawData answer for each done item")
    args = p.parse_args()

    ws = Path(args.workspace).expanduser().resolve()
    try:
        path, state = load_state(ws, args.subject)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 1
    mode = state.get("mode")
    if mode not in OUTLINE:
        print(f"ERROR unknown mode {mode!r}", file=sys.stderr)
        return 1

    expected = OUTLINE[mode]
    coverage = state.get("coverage") or []
    by_id = {c["id"]: c for c in coverage if isinstance(c, dict) and "id" in c}

    errors: list[str] = []
    warnings: list[str] = []

    missing = [q for q in expected if q not in by_id]
    extra = [i for i in by_id if i not in expected]
    if missing:
        errors.append(f"coverage missing {len(missing)} ids: {missing[:8]}{'...' if len(missing)>8 else ''}")
    if extra:
        warnings.append(f"coverage has {len(extra)} non-outline ids: {extra[:8]}")

    pending = [q for q in expected if by_id.get(q, {}).get("status") != "done"]
    done = [q for q in expected if by_id.get(q, {}).get("status") == "done"]

    raw = state.get("rawData") or {}
    void_in_raw = [q for q in VOID_IDS if q in raw]
    void_in_cov = [q for q in by_id if is_void(q)]
    if void_in_raw:
        errors.append(f"rawData contains void ids Q61–Q73: {void_in_raw}")
    if void_in_cov:
        errors.append(f"coverage contains void ids: {void_in_cov}")

    # quick→core residue: Q96 may live in rawData while mode=core
    if mode == "core" and "Q96" in raw and "Q96" not in by_id:
        warnings.append("Q96 present in rawData but not in core coverage (expected after quick→core)")

    if args.strict_raw:
        for q in done:
            ans = raw.get(q)
            if not isinstance(ans, dict) or not str(ans.get("answer") or "").strip():
                errors.append(f"{q} status=done but rawData empty")

    for q, item in by_id.items():
        try:
            mo = module_of(q)
        except KeyError as e:
            errors.append(f"bad id in coverage: {q} ({e})")
            continue
        if item.get("module") and item["module"] != mo:
            errors.append(f"{q} module mismatch {item.get('module')} != {mo}")

    turns = state.get("dialogueTurns") or []
    print(f"state: {path}")
    print(f"mode: {mode}")
    print(f"coverage: {len(done)}/{len(expected)} done")
    print(f"dialogueTurns: {len(turns)}")
    print(f"pending: {len(pending)}")
    if pending and len(pending) <= 20:
        print("pending_ids:", ", ".join(pending))
    elif pending:
        print("pending_ids (head):", ", ".join(pending[:20]), "...")

    for w in warnings:
        print(f"WARN {w}")
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)

    if errors:
        return 1
    if pending:
        print("RESULT incomplete")
        return 0
    print("RESULT complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
