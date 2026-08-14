# Upload contents

## Included by whitelist

- anonymous Python reference harness;
- standard-library unit tests;
- GitHub Actions syntax and smoke-test workflow;
- method pseudocode and evidence-boundary documentation;
- path-parameterized scripts for the completed public external adversarial ablation;
- frozen public-proxy run-level CSVs, aggregate tables, cost audit, input hashes, and reproduction checks;
- public dataset links, identifiers, citations, and reuse notes;
- restricted-data availability statement;
- privacy-conscious `.gitignore` and third-party notice;
- final checksum manifest generated after validation.

## Deliberately excluded

- manuscripts, rebuttals, checklists, PDFs, Word files, and rendered figures;
- original restricted A3 data, raw public-dataset downloads, and derived spatial geometries;
- model weights, checkpoints, embeddings, caches, logs, and any run outputs outside the whitelisted external-ablation tables;
- A3 run outputs, manuscript tables, and paper-specific build scripts;
- planner questionnaires, participant records, demographics, interviews, consent, or ethics records;
- author names, affiliations, emails, account names, local absolute paths, and credentials;
- archives and Git metadata inside the upload directory.

## Scientific status

The root package remains a reference harness for the planner-exclusion rerun loop. The `external_ablation` subdirectory contains actual public-proxy adversarial-ablation results and scripts, but it is not the unavailable original A3 GATv2–NSGA-II–SHAP/LIME implementation and cannot substantiate the restricted A3 metrics.
