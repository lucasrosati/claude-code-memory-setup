#!/usr/bin/env python3
"""Summarize paired, normalized usage ledgers; never invoke a model."""
import argparse
import json
from pathlib import Path

FIELDS = ("input_uncached", "input_cache_read", "input_cache_write", "output")


def summarize(records):
    totals = {}
    seen = set()
    for row in records:
        key = (row["scope"], row["pair"], row["arm"])
        if key[0] not in ("query", "session") or key[2] not in ("baseline", "memory"):
            raise ValueError("scope must be query/session; arm must be baseline/memory")
        identity = (*key, row["request_id"])
        if identity in seen:
            raise ValueError("duplicate request within an arm and scope")
        seen.add(identity)
        usage = row["usage"]
        if set(usage) != set(FIELDS):
            raise ValueError("usage must contain exactly the four disjoint token fields")
        if any(type(usage[f]) is not int or usage[f] < 0 for f in FIELDS):
            raise ValueError("token counts must be non-negative integers")
        bucket = totals.setdefault(key, dict.fromkeys(FIELDS, 0))
        for field in FIELDS:
            bucket[field] += usage[field]
    results = []
    for scope, pair in sorted({key[:2] for key in totals}):
        arms = {}
        for arm in ("baseline", "memory"):
            if (scope, pair, arm) not in totals:
                raise ValueError(f"unpaired measurement: {scope}/{pair}/{arm}")
            arms[arm] = totals[(scope, pair, arm)]
        baseline = sum(arms["baseline"].values())
        memory = sum(arms["memory"].values())
        results.append({"scope": scope, "pair": pair, "usage": arms,
                        "total_tokens": {"baseline": baseline, "memory": memory},
                        "baseline_over_memory": baseline / memory if memory else None,
                        "reduction_percent": 100 * (1 - memory / baseline) if baseline else None})
    if not results:
        raise ValueError("empty ledger")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        records = [json.loads(line) for line in args.ledger.read_text().splitlines() if line.strip()]
        print(json.dumps(summarize(records), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"Invalid ledger: {error}\n")


if __name__ == "__main__":
    main()
