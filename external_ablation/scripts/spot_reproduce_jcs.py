import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


if not hasattr(np, "trapezoid"):
    np.trapezoid = np.trapz


def sorted_front(rows):
    frame = pd.DataFrame(rows)
    values = frame[["coverage", "mean_distance_km", "gini"]].to_numpy(float)
    return values[np.lexsort((values[:, 2], values[:, 1], values[:, 0]))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source_root / "src"))
    import run_jcs_campaign as campaign

    ablation = args.source_root / "artifacts" / "jcs" / "ablation_campaign_20260721"
    postmain = args.source_root / "artifacts" / "jcs" / "postmain_campaign_20260722"
    runs = [
        ablation / "context_only", ablation / "confidence_inverted",
        ablation / "graph_then_diversity", ablation / "diversity_then_graph",
        ablation / "weight_01", ablation / "weight_10",
        postmain / "corruption_025", postmain / "corruption_050",
        postmain / "corruption_100", postmain / "corruption_200",
    ]
    key = {"city": "zhaotong", "population_source": "worldpop", "edge_failure_rate": 0.0, "seed": 113}
    rows = []
    args.output.mkdir(parents=True, exist_ok=True)
    for run in runs:
        config = json.loads((run / "run_manifest.json").read_text(encoding="utf-8"))["config"]
        meta = campaign.condition_meta(key["city"], key["population_source"], key["edge_failure_rate"], key["seed"], config)
        result = campaign.run_condition(meta, config, campaign.controller_table(config))
        fresh_metric = result["metrics"][0]
        archived_metrics = pd.read_csv(run / "method_metrics.csv")
        mask = (
            (archived_metrics.city == key["city"])
            & (archived_metrics.population_source == key["population_source"])
            & (archived_metrics.edge_failure_rate == key["edge_failure_rate"])
            & (archived_metrics.seed == key["seed"])
        )
        archived_metric = archived_metrics[mask].iloc[0]
        archived_fronts = pd.read_csv(run / "pareto_points.csv.gz")
        mask_front = (
            (archived_fronts.city == key["city"])
            & (archived_fronts.population_source == key["population_source"])
            & (archived_fronts.edge_failure_rate == key["edge_failure_rate"])
            & (archived_fronts.seed == key["seed"])
        )
        old_front = sorted_front(archived_fronts[mask_front])
        new_front = sorted_front(result["fronts"])
        metrics = ["coverage", "mean_distance_km", "gini", "hv", "igd_plus", "objective_evaluations"]
        rows.append({
            "run": run.name,
            "variant": config.get("variant"),
            "structure": config.get("structure"),
            "positive_loss_weight": config.get("positive_loss_weight"),
            "embedding_corruption": config.get("embedding_corruption", 0.0),
            "metric_max_absolute_difference": max(abs(float(fresh_metric[m]) - float(archived_metric[m])) for m in metrics),
            "front_rows_archive": len(old_front),
            "front_rows_rerun": len(new_front),
            "front_max_absolute_difference": float(np.max(np.abs(old_front - new_front))) if old_front.shape == new_front.shape else None,
        })
        print(f"spot rerun {run.name} complete", flush=True)
    report = pd.DataFrame(rows)
    report.to_csv(args.output / "jcs_spot_reproduction.csv", index=False)
    summary = {
        "condition": key,
        "runs": len(report),
        "tolerance": 1e-12,
        "metrics_reproduced_within_tolerance": int((report.metric_max_absolute_difference <= 1e-12).sum()),
        "fronts_reproduced_within_tolerance": int((report.front_max_absolute_difference <= 1e-12).sum()),
    }
    (args.output / "jcs_spot_reproduction.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
