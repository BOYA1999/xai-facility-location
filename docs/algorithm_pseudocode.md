# Full workflow protocol pseudocode

This document specifies the intended full experimental workflow. It is not executable code and must not be cited as evidence that the unavailable original experiments were rerun.

```text
INPUT:
    grid features X, road graph G, demand weights n, candidate mask g
    facility budget p = 15, service threshold = 5 km
    blocked split seed = 2026, optimization seeds = 0..29
    optional external risk layer R_ext supplied by planners

BLOCK_SPLIT(G, 10 x 10, 60:20:20)
REMOVE_MESSAGE_EDGES_ACROSS_SPLITS(G)

TRAIN_GATV2:
    build road-connected positive pairs
    build distant functionally-similar triplets
    minimize (1-lambda)*L_spatial + lambda*L_triplet + 1e-4*||theta||^2
    AdamW(lr=1e-3, weight_decay=1e-4), at most 500 epochs
    early stop after 50 validation epochs without improvement
    return fixed 32-dimensional embeddings Z

FOR seed IN 0..29:
    initialize 100 embedding-guided and 100 uniformly random facility sets
    RUN_NSGAII(population=200, generations=500):
        evaluate coverage, mean road distance, and weighted Gini
        crossover with probability 0.90
        mutate each facility with probability 1/15
        with probability 0.70 choose replacement from five nearest feasible cells in Z
        otherwise choose from all feasible cells
        preserve hard masks, exactly p facilities, and 2-km spacing
        stop only after hypervolume changes <0.1% for 50 generations
    save every seed-level metric and final nondominated set

FIT_XGBOOST_SURROGATE on training blocks only
COMPUTE_SHAP with adjacent-cell background
COMPUTE_LIME with 100 road-nearest neighbors and 200 perturbations
SCREEN 100 counterfactual scenarios with the surrogate

PLANNER_REVIEW:
    inspect the AI proposal and explanations
    identify missing external constraints
    if an external risk layer is relevant:
        update g := g AND NOT R_ext
        batch the five selected counterfactual validations
        reuse Z and a common warm-start population
        rerun NSGA-II within the 4.3-min XAI block
    planner chooses ACCEPT, REVISE, or REJECT

ADVERSARIAL_ABLATION:
    for representation in {GATv2, matched GraphSAGE, matched GCN, matched residual MLP}:
        require parameters within 1%, MACs within 5%, and time within 5%
        repeat the same 30 paired seeds
    for structure in {serial, parallel fusion, post-search reranking, SHAP-weighted mutation}:
        hold objective-evaluation count fixed and repeat the same seeds
    for loss ratio in {10:1, 7:3, 1:1, 3:7, 1:10}:
        repeat the same seeds
    for each frozen failure stressor and level:
        repeat the same seeds
        register the first prespecified collapse point

OUTPUT:
    seed-level results, paired intervals, Holm-adjusted tests
    parameter/MAC/time audit
    sensitivity curves and failure maps
    AI proposal, planner-added constraint, rerun result, and final planner decision
```

