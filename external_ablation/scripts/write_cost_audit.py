import argparse
import json
import sys
from pathlib import Path

import numpy as np


if not hasattr(np, "trapezoid"):
    np.trapezoid = np.trapz


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-code", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--script-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path[:0] = [str(args.source_code), str(args.script_dir)]
    import run_public_rerun as rerun
    import run_repeated_ablation as repeated
    import run_matched_replacements as matched

    cfg, _, demand, _, _ = repeated.load_archived_inputs(args.source_run)
    features = repeated.build_demand_features(demand)
    constructors = {
        "GAT": lambda: rerun.DenseGAT(features.shape[1], cfg.gat_hidden, cfg.gat_output),
        "GCN": lambda: matched.GCN(features.shape[1], cfg.gat_output),
        "GraphSAGE": lambda: matched.SAGE(features.shape[1], cfg.gat_output),
        "MLP+fixed diffusion": lambda: matched.MLP(features.shape[1], cfg.gat_output),
    }
    models = {name: constructor() for name, constructor in constructors.items()}
    reference_parameters = matched.parameter_count(models["GAT"])
    reference_macs = matched.macs("GAT", len(features), features.shape[1], cfg.gat_output)
    audit = []
    for name, model in models.items():
        parameters = matched.parameter_count(model)
        operations = matched.macs(name.split("+")[0], len(features), features.shape[1], cfg.gat_output)
        audit.append({
            "module": name,
            "parameters": parameters,
            "parameter_delta_fraction": (parameters - reference_parameters) / reference_parameters,
            "macs": operations,
            "mac_delta_fraction": (operations - reference_macs) / reference_macs,
            "parameter_gate": abs(parameters - reference_parameters) / reference_parameters <= 0.01,
            "mac_gate": abs(operations - reference_macs) / reference_macs <= 0.05,
        })
    args.output.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
