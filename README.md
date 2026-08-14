# Explainable Facility Location — Reference Release

This repository is an anonymous reference release for an AI-assisted emergency-facility-location workflow. It contains a data-free planner-in-the-loop harness and a separately labeled external public-data adversarial-ablation archive.

## Evidence boundary

The original training code, run-level outputs, model weights, and restricted Guangzhou input layers were not present in the revision archive used to prepare this release. Consequently:

- this repository is **not** the original experiment archive;
- it does **not** reproduce the restricted A3 numerical results reported in the manuscript;
- `xai_facility_location` is a deterministic, standard-library reference harness using Euclidean distance and greedy maximum coverage;
- the documented A3 GATv2, NSGA-II, SHAP, and LIME workflow is supplied only as protocol pseudocode in [`docs/algorithm_pseudocode.md`](docs/algorithm_pseudocode.md);
- [`external_ablation`](external_ablation/README.md) contains actual public-proxy run outputs and path-parameterized scripts. Its 4-km, 12-facility, two-layer GAT contract differs from the restricted A3 500-m, 15-facility, three-layer GATv2 contract.

This boundary prevents reconstructed code from being presented as a rerun of unavailable experiments.

## Quick start

Python 3.10 or later is required. The reference harness has no runtime dependencies outside the Python standard library.

```bash
python -m xai_facility_location --help
python -m xai_facility_location smoke --seed 2026
python -m unittest discover -s tests -v
```

The smoke command generates synthetic cells in memory. It downloads and writes no data.

## Run with user-supplied cells

Prepare a CSV outside the repository with these columns:

| Column | Type | Meaning |
|---|---|---|
| `cell_id` | string | Unique, non-sensitive cell identifier |
| `x_km` | number | Projected x coordinate in kilometres |
| `y_km` | number | Projected y coordinate in kilometres |
| `demand` | number | Non-negative demand weight |
| `hazard` | number | Non-negative screening score used only for deterministic tie-breaking |
| `feasible` | boolean | `true/false`, `yes/no`, or `1/0` |

Example:

```bash
python -m xai_facility_location run \
  --input user_cells.csv \
  --budget 15 \
  --service-km 5 \
  --min-spacing-km 2 \
  --exclude cell_001 \
  --exclude cell_017
```

The command prints JSON to standard output. It does not persist the input or output. Do not commit private source files or generated results.

## Data sources cited by the study

No dataset is bundled or downloaded by this repository. The public hazard datasets cited for external failure-boundary stress tests, together with their identifiers and reuse limits, are documented in [`DATASETS.md`](DATASETS.md). Restricted Guangzhou road-network, census-block, and disaster-risk inputs are documented separately in [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md).

The public hazard overlays are stress-test inputs; they are not substitutes for, or validation of, the restricted Guangzhou layers.

## Real external adversarial ablation

The release includes frozen run-level CSVs for the 30-seed equal-parameter/equal-MAC representation replacement, the five-level public-proxy loss-weight curve, the original public Guangzhou paired baseline, 20-city structure/order variants, four embedding-corruption levels, and fixed-condition reproduction checks. See [`external_ablation/README.md`](external_ablation/README.md) for commands, provenance, dependencies, and evidence limits.

## Privacy and release status

This release excludes manuscripts, participant materials, raw third-party data, model weights, caches, logs, Git metadata, author identifiers, email addresses, credentials, and local absolute paths. It includes only the public external-ablation run tables and input checksums listed in [`UPLOAD_CONTENTS.md`](UPLOAD_CONTENTS.md).

No software license has yet been authorized for this reconstructed release. Resolve [`LICENSE_SELECTION_REQUIRED.md`](LICENSE_SELECTION_REQUIRED.md) before treating the repository as open source.
