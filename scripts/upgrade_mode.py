#!/usr/bin/env python3
"""Upgrade interview state mode and rebuild coverage (preserves rawData)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outline_data import OUTLINE, rebuild_coverage_for_upgrade  # noqa: E402
from validate_coverage import load_state  # noqa: E402

ORDER = {"quick": 0, "core": 1, "deep": 2}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--to", required=True, choices=["quick", "core", "deep"])
    p.add_argument("--allow-downgrade", action="store_true")
    args = p.parse_args()

    ws = Path(args.workspace).expanduser().resolve()
    try:
        path, state = load_state(ws, args.subject)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 1
    cur = state.get("mode")
    if cur not in OUTLINE:
        print(f"ERROR bad current mode {cur!r}", file=sys.stderr)
        return 1
    if ORDER[args.to] < ORDER[cur] and not args.allow_downgrade:
        print(f"ERROR refuse downgrade {cur} → {args.to} (pass --allow-downgrade)", file=sys.stderr)
        return 2
    if args.to == cur:
        print(f"NOOP already {cur}")
        return 0

    old_cov = state.get("coverage") or []
    if old_cov and not all(c.get("status") == "done" for c in old_cov):
        pending = sum(1 for c in old_cov if c.get("status") != "done")
        print(
            f"WARN current {cur} coverage incomplete ({pending} pending); "
            f"upgrade still allowed; completedModes will not record {cur}",
            file=sys.stderr,
        )

    new_state = rebuild_coverage_for_upgrade(state, args.to)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    new_state.setdefault("metadata", {})["updatedAt"] = now
    path.write_text(json.dumps(new_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cov = new_state["coverage"]
    done = sum(1 for c in cov if c["status"] == "done")
    print(f"OK {path}")
    print(f"{cur} → {args.to} coverage {done}/{len(cov)}")
    # highlight Q96 fate
    q96_raw = bool((new_state.get("rawData") or {}).get("Q96", {}).get("answer"))
    q96_in = any(c["id"] == "Q96" for c in cov)
    print(f"Q96 in rawData={q96_raw} in_coverage={q96_in}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
