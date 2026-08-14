# Real public-proxy adversarial ablation

This directory contains the actual external adversarial-ablation outputs used in the revision. It does not reproduce the restricted A3 case.

## Frozen scientific boundary

- Public Guangzhou proxy: 4-km grid, 89 demand cells, 80 candidate sites, 12 selected facilities, 5-km threshold, two-layer 16-dimensional GAT, 180 epochs, and NSGA-II population 80 for 60 generations.
- Restricted A3 case: 500-m grid, 15 facilities, three-layer 32-dimensional GATv2, and NSGA-II population 200 for 500 generations.
- Therefore the results below test mechanism transfer and failure boundaries only. They do not replace the A3 point estimates or 45-min runtime.

## Included evidence

- `results/matched_replacement_30_seed_results.csv`: GAT, GCN, GraphSAGE, and fixed-diffusion MLP under the same 30 seeds.
- `results/cost_audit.json`: 729-736 parameters and 432,807-456,570 MACs; every module passes the 1% parameter and 5% MAC gates.
- `results/matched_replacement_inference.csv`: paired bootstrap intervals, Wilcoxon tests, and Holm correction across nine tests.
- `results/loss_weight_20_seed_results.csv`: five positive-edge:negative-edge weights over 20 paired seeds.
- `results/paired_30_seed_results.csv`: public Guangzhou GAT-guided and plain NSGA-II paired baseline.
- `results/twenty_city_structural_ablation.csv` and `results/corruption_paired.csv`: 20-city order/weight and embedding-corruption evidence.
- `results/guangzhou_reproduction_check.json` and `results/jcs_spot_reproduction.json`: negative and exact reproduction checks; the Guangzhou graph-structure archive is not marked fully reproduced because two seed-1007 trajectories differed.

## Main results

- Mean coverage was 71.08% for GAT, 72.12% for GCN, 72.11% for GraphSAGE, and 72.43% for fixed-diffusion MLP. No contrast across coverage, distance, and Gini survived Holm correction.
- GAT-guided coverage was 1.85 percentage points below plain NSGA-II in the public Guangzhou run (`p=0.0209`).
- The strongest 20-city failure was `diversity_to_graph`: delta HV=-0.158252 and delta IGD+=+0.027819.
- No prespecified statistical collapse was detected from 0.25 to 2.00 embedding SD; this censors the tested threshold above 2 SD rather than proving robustness.

## Dependencies

Use Python 3.10 or later with:

```text
numpy==2.4.6
pandas==3.0.3
scipy==1.18.0
torch==2.13.0
```

The source experiment workspaces also use the packages listed in `requirements-source-workspaces.txt`.

## Re-execution

The scripts use only command-line paths and contain no account names or local absolute paths. Example:

```bash
python external_ablation/scripts/run_matched_replacements.py \
  --source-code /path/to/public-guangzhou-workspace \
  --source-run /path/to/archived-public-guangzhou-run \
  --output external_ablation/new_results/matched \
  --seeds 30
```

The imported source modules and raw third-party data are not redistributed here because their reusable software/data license was not established from the supplied folders. The included result CSVs and input hashes preserve the audit trail; the repository owner must select a release license before publication.

## Public data sources

The completed experiments cite OpenStreetMap, WorldPop 2020, GHS-POP R2023A, and USGS ShakeMap. Exact product links, citations, and evidence limitations are in [`../DATASETS.md`](../DATASETS.md). No raw dataset is included.
