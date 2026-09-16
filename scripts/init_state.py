#!/usr/bin/env python3
"""Initialize expression-audit state under workspace/expression-audit/."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline_data import OUTLINE, aggregate_progress, build_coverage, slug  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    p = argparse.ArgumentParser(description="Init self-expression-audit state")
    p.add_argument("--workspace", required=True, help="Workspace root")
    p.add_argument("--subject", required=True)
    p.add_argument("--mode", choices=["quick", "core", "deep"], default="core")
    p.add_argument("--force", action="store_true", help="Overwrite existing state")
    args = p.parse_args()

    ws = Path(args.workspace).expanduser().resolve()
    root = ws / "expression-audit"
    root.mkdir(parents=True, exist_ok=True)
    (root / "exports").mkdir(exist_ok=True)

    name = slug(args.subject)
    state_path = root / f"{name}.state.json"
    if state_path.exists() and not args.force:
        print(f"EXISTS {state_path}", file=sys.stderr)
        print("Use --force to overwrite, or pick another --subject.", file=sys.stderr)
        return 2

    coverage = build_coverage(args.mode)
    now = utc_now()
    state = {
        "version": "2.1",
        "subject": args.subject.strip(),
        "mode": args.mode,
        "completedModes": [],
        "progress": aggregate_progress(coverage),
        "coverage": coverage,
        "thread": {
            "theme": "",
            "openLoops": [],
            "lastQuestionId": None,
            "lastUserSignal": None,
            "priority": "normal",
        },
        "dialogueTurns": [],
        "prototypeAnchors": {
            "anchor1": {"status": "pending"},
            "anchor2": {"status": "pending"},
            "anchor3": {"status": "pending"},
        },
        "tensionLog": [],
        "coreIdentity": None,
        "quickReference": None,
        "fourSentences": None,
        "resonanceLog": [],
        "resonancePoints": [],
        "candidateNorthStar": None,
        "northStarLoop": None,
        "northStarHistory": [],
        "knowledgeGraph": None,
        "learningPath": None,
        "rawData": {},
        "outputs": {
            "dialoguePath": None,
            "auditPath": None,
            "compiledAt": None,
            "modeAtCompile": None,
        },
        "storage": {
            "rootDir": str(root),
            "migratedFrom": None,
        },
        "metadata": {
            "createdAt": now,
            "updatedAt": now,
            "sessionCount": 0,
            "lastModuleRun": None,
            "notes": "",
            "engine": "interview-v2",
            "lastTurn": 0,
        },
    }

    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {state_path}")
    print(f"mode={args.mode} coverage={len(OUTLINE[args.mode])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
