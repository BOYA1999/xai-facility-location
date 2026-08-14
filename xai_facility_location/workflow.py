from __future__ import annotations

import csv
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Cell:
    cell_id: str
    x_km: float
    y_km: float
    demand: float
    hazard: float
    feasible: bool


@dataclass(frozen=True)
class PlanMetrics:
    coverage: float
    mean_distance_km: float
    distance_gini: float


@dataclass(frozen=True)
class Plan:
    selected_ids: tuple[str, ...]
    metrics: PlanMetrics

    def to_dict(self) -> dict[str, object]:
        return {"selected_ids": list(self.selected_ids), "metrics": asdict(self.metrics)}


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def load_cells(path: str | Path) -> list[Cell]:
    required = {"cell_id", "x_km", "y_km", "demand", "hazard", "feasible"}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
        cells = [
            Cell(
                cell_id=row["cell_id"].strip(),
                x_km=float(row["x_km"]),
                y_km=float(row["y_km"]),
                demand=float(row["demand"]),
                hazard=float(row["hazard"]),
                feasible=_parse_bool(row["feasible"]),
            )
            for row in reader
        ]
    _validate_cells(cells)
    return cells


def _validate_cells(cells: list[Cell]) -> None:
    if not cells:
        raise ValueError("at least one cell is required")
    ids = [cell.cell_id for cell in cells]
    if any(not cell_id for cell_id in ids):
        raise ValueError("cell_id must not be blank")
    if len(ids) != len(set(ids)):
        raise ValueError("cell_id values must be unique")
    if any(cell.demand < 0 or cell.hazard < 0 for cell in cells):
        raise ValueError("demand and hazard must be non-negative")
    if sum(cell.demand for cell in cells) <= 0:
        raise ValueError("total demand must be positive")


def _distance(a: Cell, b: Cell) -> float:
    return math.hypot(a.x_km - b.x_km, a.y_km - b.y_km)


def _weighted_gini(values: list[float], weights: list[float]) -> float:
    pairs = sorted(zip(values, weights), key=lambda pair: pair[0])
    total_weight = sum(weights)
    weighted_sum = sum(value * weight for value, weight in pairs)
    if total_weight <= 0 or weighted_sum <= 0:
        return 0.0
    cumulative_weight = 0.0
    cumulative_weighted_value = 0.0
    pair_sum = 0.0
    for value, weight in pairs:
        pair_sum += weight * (value * cumulative_weight - cumulative_weighted_value)
        cumulative_weight += weight
        cumulative_weighted_value += value * weight
    return pair_sum / (total_weight * weighted_sum)


def _metrics(cells: list[Cell], selected: list[Cell], service_km: float) -> PlanMetrics:
    nearest = [min(_distance(cell, facility) for facility in selected) for cell in cells]
    total_demand = sum(cell.demand for cell in cells)
    covered = sum(cell.demand for cell, distance in zip(cells, nearest) if distance <= service_km)
    mean_distance = sum(cell.demand * distance for cell, distance in zip(cells, nearest)) / total_demand
    gini = _weighted_gini(nearest, [cell.demand for cell in cells])
    return PlanMetrics(
        coverage=covered / total_demand,
        mean_distance_km=mean_distance,
        distance_gini=gini,
    )


def select_sites(
    cells: list[Cell],
    budget: int,
    service_km: float,
    min_spacing_km: float,
    excluded_ids: Iterable[str] = (),
) -> Plan:
    _validate_cells(cells)
    if budget < 1 or service_km <= 0 or min_spacing_km < 0:
        raise ValueError("budget and service_km must be positive; min_spacing_km must be non-negative")
    excluded = set(excluded_ids)
    candidates = [cell for cell in cells if cell.feasible and cell.cell_id not in excluded]
    if len(candidates) < budget:
        raise ValueError("fewer feasible, non-excluded candidates than the facility budget")

    selected: list[Cell] = []
    uncovered = {cell.cell_id for cell in cells}
    for _ in range(budget):
        allowed = [
            candidate
            for candidate in candidates
            if candidate not in selected
            and all(_distance(candidate, chosen) >= min_spacing_km for chosen in selected)
        ]
        if not allowed:
            raise ValueError("minimum spacing leaves too few candidates for the requested budget")

        def score(candidate: Cell) -> tuple[float, float, str]:
            marginal = sum(
                cell.demand
                for cell in cells
                if cell.cell_id in uncovered and _distance(cell, candidate) <= service_km
            )
            return marginal, -candidate.hazard, candidate.cell_id

        chosen = max(allowed, key=score)
        selected.append(chosen)
        uncovered = {
            cell_id
            for cell_id in uncovered
            if _distance(next(cell for cell in cells if cell.cell_id == cell_id), chosen) > service_km
        }

    return Plan(tuple(cell.cell_id for cell in selected), _metrics(cells, selected, service_km))


def planner_rerun(
    cells: list[Cell],
    budget: int,
    service_km: float,
    min_spacing_km: float,
    planner_excluded_ids: Iterable[str],
) -> dict[str, object]:
    excluded = tuple(sorted(set(planner_excluded_ids)))
    initial = select_sites(cells, budget, service_km, min_spacing_km)
    revised = select_sites(cells, budget, service_km, min_spacing_km, excluded)
    return {
        "status": "reference_harness_only",
        "distance_model": "euclidean_km_not_road_network",
        "planner_excluded_ids": list(excluded),
        "initial_plan": initial.to_dict(),
        "revised_plan": revised.to_dict(),
    }


def synthetic_cells(seed: int, side: int = 10) -> list[Cell]:
    rng = random.Random(seed)
    cells = [
        Cell(
            cell_id=f"synthetic_{row:02d}_{column:02d}",
            x_km=float(column),
            y_km=float(row),
            demand=float(rng.randint(20, 200)),
            hazard=round(rng.random(), 6),
            feasible=rng.random() > 0.08,
        )
        for row in range(side)
        for column in range(side)
    ]
    _validate_cells(cells)
    return cells


def smoke_result(seed: int) -> dict[str, object]:
    cells = synthetic_cells(seed)
    initial = select_sites(cells, budget=6, service_km=2.5, min_spacing_km=1.5)
    excluded = max(
        (cell for cell in cells if cell.cell_id in initial.selected_ids),
        key=lambda cell: cell.hazard,
    ).cell_id
    result = planner_rerun(cells, 6, 2.5, 1.5, [excluded])
    result["input"] = {"kind": "synthetic", "seed": seed, "cell_count": len(cells)}
    return result

