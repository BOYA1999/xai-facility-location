import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import wilcoxon


if not hasattr(np, "trapezoid"):
    np.trapezoid = np.trapz


class GCN(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.one = nn.Linear(in_dim, 34)
        self.two = nn.Linear(34, out_dim)

    def forward(self, x, adjacency):
        h = F.elu(self.one(adjacency @ x))
        return F.normalize(self.two(adjacency @ h), p=2, dim=1)


class SAGE(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.one = nn.Linear(2 * in_dim, 17)
        self.two = nn.Linear(34, out_dim)
        self.scale = nn.Parameter(torch.ones(out_dim))

    def forward(self, x, adjacency):
        h = F.elu(self.one(torch.cat([x, adjacency @ x], dim=1)))
        smooth = 0.5 * (h[:, :10] + adjacency @ h[:, :10])
        h = torch.cat([smooth, h[:, 10:]], dim=1)
        z = self.two(torch.cat([h, adjacency @ h], dim=1))
        z = 0.5 * (z + adjacency @ z)
        return F.normalize(z * self.scale, p=2, dim=1)


class MLP(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.one = nn.Linear(in_dim, 34)
        self.two = nn.Linear(34, out_dim)

    def forward(self, x, adjacency):
        z = self.two(F.elu(self.one(x)))
        for _ in range(3):
            z = 0.5 * (z + adjacency @ z)
        return F.normalize(z, p=2, dim=1)


def reset(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def normalize_adjacency(adjacency):
    matrix = torch.tensor(adjacency, dtype=torch.float32)
    degree = matrix.sum(dim=1).clamp_min(1.0).pow(-0.5)
    return degree[:, None] * matrix * degree[None, :]


def train(model, features, adjacency, epochs, learning_rate, positive_weight=1.0, normalize_loss=True):
    x = torch.tensor(features, dtype=torch.float32)
    graph = torch.tensor(adjacency, dtype=torch.bool) if model.__class__.__name__ == "DenseGAT" else normalize_adjacency(adjacency)
    positives = np.argwhere(np.triu(adjacency, 1) > 0)
    positive_set = set(map(tuple, positives.tolist()))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    started = time.perf_counter()
    for _ in range(epochs):
        negatives = []
        while len(negatives) < len(positives):
            i, j = np.random.randint(0, len(features), size=2)
            if i != j and (min(i, j), max(i, j)) not in positive_set:
                negatives.append((i, j))
        negatives = np.asarray(negatives, dtype=int)
        embedding = model(x, graph)
        positive_score = (embedding[positives[:, 0]] * embedding[positives[:, 1]]).sum(dim=1)
        negative_score = (embedding[negatives[:, 0]] * embedding[negatives[:, 1]]).sum(dim=1)
        loss = -(
            positive_weight * F.logsigmoid(positive_score).mean()
            + F.logsigmoid(-negative_score).mean()
        )
        if normalize_loss:
            loss = loss / (positive_weight + 1.0)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    seconds = time.perf_counter() - started
    with torch.no_grad():
        return model(x, graph).cpu().numpy(), seconds, float(loss)


def parameter_count(model):
    return sum(parameter.numel() for parameter in model.parameters())


def macs(name, nodes, in_dim, out_dim):
    if name == "GAT":
        return nodes * in_dim * 32 + 2 * nodes * 32 + nodes * nodes * 32 + nodes * 32 * out_dim + 2 * nodes * out_dim + nodes * nodes * out_dim
    if name == "GCN":
        return nodes * in_dim * 34 + nodes * nodes * 34 + nodes * 34 * out_dim + nodes * nodes * out_dim
    if name == "GraphSAGE":
        return nodes * nodes * in_dim + nodes * 2 * in_dim * 17 + nodes * nodes * 17 + nodes * 34 * out_dim + nodes * nodes * 10 + nodes * nodes * out_dim
    return nodes * in_dim * 34 + nodes * 34 * out_dim + 3 * nodes * nodes * out_dim


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-code", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, default=30)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source_code))
    import run_public_rerun as rerun
    import run_repeated_ablation as repeated

    args.output.mkdir(parents=True, exist_ok=True)
    cfg, _, demand, candidates, distance = repeated.load_archived_inputs(args.source_run)
    features = repeated.build_demand_features(demand)
    adjacency = repeated.graph_adjacency(demand, features, "full")
    candidate_features, nearest = repeated.build_candidate_features(demand, candidates, distance)
    weights = demand["population"].to_numpy(dtype=float)
    constructors = {
        "GAT": lambda: rerun.DenseGAT(features.shape[1], cfg.gat_hidden, cfg.gat_output),
        "GCN": lambda: GCN(features.shape[1], cfg.gat_output),
        "GraphSAGE": lambda: SAGE(features.shape[1], cfg.gat_output),
        "MLP+fixed diffusion": lambda: MLP(features.shape[1], cfg.gat_output),
    }
    seeds = ([42] + list(range(1001, 1030)))[: args.seeds]
    rows = []
    for seed in seeds:
        for name, constructor in constructors.items():
            reset(seed)
            embedding, train_seconds, loss = train(constructor(), features, adjacency, cfg.gat_epochs, cfg.gat_lr)
            candidate_embedding = repeated.candidate_embeddings(embedding, nearest, candidate_features)
            reset(seed)
            started = time.perf_counter()
            solution = repeated.best_from_nsga("guided", distance, weights, cfg, candidate_embedding)
            search_seconds = time.perf_counter() - started
            coverage, mean_distance, gini = solution["metrics"]
            rows.append({
                "seed": seed, "module": name, "coverage": coverage, "mean_distance": mean_distance,
                "gini": gini, "training_loss": loss, "train_seconds": train_seconds,
                "search_seconds": search_seconds, "total_seconds": train_seconds + search_seconds,
                "selected_indices": " ".join(map(str, solution["selected"])),
            })
        print(f"matched replacement seed {seed} complete", flush=True)
    raw = pd.DataFrame(rows)
    raw.to_csv(args.output / "matched_replacement_30_seed_results.csv", index=False)
    summary = raw.groupby("module", as_index=False).agg(
        coverage_mean=("coverage", "mean"), coverage_sd=("coverage", "std"),
        distance_mean=("mean_distance", "mean"), distance_sd=("mean_distance", "std"),
        gini_mean=("gini", "mean"), gini_sd=("gini", "std"),
        train_seconds_mean=("train_seconds", "mean"), total_seconds_mean=("total_seconds", "mean"),
    )
    summary.to_csv(args.output / "matched_replacement_summary.csv", index=False)
    reference = raw[raw.module == "GAT"].set_index("seed")
    tests = []
    for name in constructors:
        if name == "GAT":
            continue
        candidate = raw[raw.module == name].set_index("seed")
        for metric in ["coverage", "mean_distance", "gini"]:
            delta = candidate[metric] - reference[metric]
            statistic, p_value = wilcoxon(candidate[metric], reference[metric])
            tests.append({"module": name, "metric": metric, "mean_delta_vs_gat": delta.mean(), "wilcoxon_statistic": statistic, "wilcoxon_p": p_value})
    pd.DataFrame(tests).to_csv(args.output / "matched_replacement_paired_tests.csv", index=False)
    models = {name: constructor() for name, constructor in constructors.items()}
    reference_parameters = parameter_count(models["GAT"])
    reference_macs = macs("GAT", len(features), features.shape[1], cfg.gat_output)
    audit = []
    for name, model in models.items():
        count = parameter_count(model)
        operations = macs(name.split("+")[0], len(features), features.shape[1], cfg.gat_output)
        audit.append({
            "module": name, "parameters": count, "parameter_delta_fraction": (count - reference_parameters) / reference_parameters,
            "macs": operations, "mac_delta_fraction": (operations - reference_macs) / reference_macs,
            "parameter_gate": abs(count - reference_parameters) / reference_parameters <= 0.01,
            "mac_gate": abs(operations - reference_macs) / reference_macs <= 0.05,
        })
    (args.output / "cost_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
