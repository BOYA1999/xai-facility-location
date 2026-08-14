from __future__ import annotations

import argparse
import json
from typing import Sequence

from .workflow import load_cells, planner_rerun, smoke_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xai-facility-location",
        description="Data-free reference harness for planner-guided facility-location reruns.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke = subparsers.add_parser("smoke", help="run an in-memory synthetic demonstration")
    smoke.add_argument("--seed", type=int, default=2026)

    run = subparsers.add_parser("run", help="run the reference harness on a user-supplied CSV")
    run.add_argument("--input", required=True)
    run.add_argument("--budget", type=int, default=15)
    run.add_argument("--service-km", type=float, default=5.0)
    run.add_argument("--min-spacing-km", type=float, default=2.0)
    run.add_argument("--exclude", action="append", default=[], metavar="CELL_ID")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "smoke":
        result = smoke_result(args.seed)
    else:
        cells = load_cells(args.input)
        result = planner_rerun(
            cells,
            args.budget,
            args.service_km,
            args.min_spacing_km,
            args.exclude,
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

