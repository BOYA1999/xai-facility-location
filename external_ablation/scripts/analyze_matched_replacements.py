import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def holm(p_values):
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(p_values) - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = pd.read_csv(args.input)
    reference = data[data.module == "GAT"].set_index("seed")
    rng = np.random.default_rng(20260813)
    rows = []
    for module in [name for name in data.module.unique() if name != "GAT"]:
        candidate = data[data.module == module].set_index("seed")
        for metric in ["coverage", "mean_distance", "gini"]:
            delta = (candidate[metric] - reference[metric]).to_numpy()
            bootstrap = delta[rng.integers(0, len(delta), (20000, len(delta)))].mean(axis=1)
            statistic, p_value = wilcoxon(candidate[metric], reference[metric])
            rows.append({
                "module": module,
                "metric": metric,
                "mean_delta_vs_gat": delta.mean(),
                "ci_low": np.quantile(bootstrap, 0.025),
                "ci_high": np.quantile(bootstrap, 0.975),
                "wilcoxon_statistic": statistic,
                "wilcoxon_p": p_value,
            })
    output = pd.DataFrame(rows)
    output["holm_p_across_9_tests"] = holm(output.wilcoxon_p.to_numpy())
    output["holm_p_within_module"] = output.groupby("module").wilcoxon_p.transform(lambda values: holm(values.to_numpy()))
    output.to_csv(args.output, index=False)
    print(output.to_string(index=False))


if __name__ == "__main__":
    main()
