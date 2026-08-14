import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch


if not hasattr(np, "trapezoid"):
    np.trapezoid = np.trapz


def reset(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-code", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--matched-script-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, default=20)
    args = parser.parse_args()
    sys.path[:0] = [str(args.source_code), str(args.matched_script_dir)]
    import run_public_rerun as rerun
    import run_repeated_ablation as repeated
    import run_matched_replacements as matched

    args.output.mkdir(parents=True, exist_ok=True)
    cfg, _, demand, candidates, distance = repeated.load_archived_inputs(args.source_run)
    features = repeated.build_demand_features(demand)
    adjacency = repeated.graph_adjacency(demand, features, "full")
    candidate_features, nearest = repeated.build_candidate_features(demand, candidates, distance)
    weights = demand["population"].to_numpy(dtype=float)
    seeds = ([42] + list(range(1001, 1020)))[: args.seeds]
    ratios = [0.1, 0.3, 1.0, 3.0, 10.0]
    rows = []
    for seed in seeds:
        for ratio in ratios:
            reset(seed)
            model = rerun.DenseGAT(features.shape[1], cfg.gat_hidden, cfg.gat_output)
            embedding, train_seconds, loss = matched.train(
                model, features, adjacency, cfg.gat_epochs, cfg.gat_lr, ratio, normalize_loss=False
            )
            candidate_embedding = repeated.candidate_embeddings(embedding, nearest, candidate_features)
            reset(seed)
            started = time.perf_counter()
            solution = repeated.best_from_nsga("guided", distance, weights, cfg, candidate_embedding)
            search_seconds = time.perf_counter() - started
            coverage, mean_distance, gini = solution["metrics"]
            rows.append({
                "seed": seed, "positive_negative_weight_ratio": ratio, "coverage": coverage,
                "mean_distance": mean_distance, "gini": gini, "training_loss": loss,
                "train_seconds": train_seconds, "search_seconds": search_seconds,
                "total_seconds": train_seconds + search_seconds,
                "selected_indices": " ".join(map(str, solution["selected"])),
            })
        print(f"loss sensitivity seed {seed} complete", flush=True)
    raw = pd.DataFrame(rows)
    raw.to_csv(args.output / "loss_weight_20_seed_results.csv", index=False)
    summary = raw.groupby("positive_negative_weight_ratio", as_index=False).agg(
        coverage_mean=("coverage", "mean"), coverage_sd=("coverage", "std"),
        distance_mean=("mean_distance", "mean"), distance_sd=("mean_distance", "std"),
        gini_mean=("gini", "mean"), gini_sd=("gini", "std"),
        train_seconds_mean=("train_seconds", "mean"), total_seconds_mean=("total_seconds", "mean"),
    )
    summary.to_csv(args.output / "loss_weight_summary.csv", index=False)
    manifest = {
        "seeds": seeds,
        "ratios": ratios,
        "interpretation": "Positive-edge to negative-edge link-prediction loss sensitivity on the external Guangzhou public-data proxy; not the A3 spatial/triplet loss.",
    }
    (args.output / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
