# External-score experiment and review redesign

Recorded October 16, 2026 before generating the new paired experiment. The earlier with-score model's AUC and 32 common rejected cases were already known; this is an exploratory extension, not an independent preregistration or confirmation.

Question: Does explaining the lender-side model leave reliance on the supplied external risk score unexplained?

Use the existing train/validation/test partition and eight-feature Random Forest settings. Train a second model adding only ExternalRiskEstimate. Explain all 40 original audited applications in both models, including applications whose simulated outcome changes; do not filter for rejection by both. Use the same 24 training record IDs as the original seed-2026 background. Original inputs and status indicators move together. The original eight-feature results must reproduce numerically.

Compute exact empirical interventional Shapley values for both models (256 and 512 coalitions). Report per-application scores, full signed contributions, grouped contributions, whether the external score is among at most four positive contributors, and outcome changes at the fixed research threshold 0.50. Report AUC on the entire original test partition, paired bootstrap AUC differences (1,000 resamples, seed 20261016), and disagreement at the threshold. Test-set permutation importance uses ten independent column permutations per input, on raw input blocks before encoding. Correlations can redistribute importance; permutation is model reliance under a defined intervention, not causal effect or upstream-score validation.

For each paired application and both models, compare five custom LIME-style fits with 1,200 independently sampled evaluation points. Reuse the original eight-feature fidelity results; evaluate nine-feature fits using the same neighborhood generator. Retain all seeds. Rank and grouping changes are descriptive across different fitted models, not interventions on a fixed lending decision and not explanations of the original model.

The HELOC data contain values of ExternalRiskEstimate but no authenticated upstream scoring model, calculation, vendor specification or upstream reason records. Do not infer these from correlated bureau features. Do not label the supplied score proprietary without evidence. Treat this as an external-score dependency whose upstream explanation is absent from this snapshot.

The workbench must distinguish model diagnosis, the recorded research decision, applicant-facing wording, and reviewer judgment. Add an external-score evidence request to downloadable reviews only when the reviewer chooses it. Explain technical terms at point of use, preserve precise methods in expandable details, and keep the primary protocol unchanged.
