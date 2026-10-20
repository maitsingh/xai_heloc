# Protocol v2: From Risk Scores to Reasons

Frozen before generating and inspecting the new experiment outputs. This is a prospective protocol for the added benchmark and reference experiment, not a preregistration of the earlier pilot. Earlier HELOC audit results and model benchmark were already known.

## Research question
Which decision-to-notice defects escape explanation-repeatability screening, and which can a structured evidence review identify?

## Two evidence tracks
1. HELOC attribution experiment: retain the original eight-feature Random Forest so its exact empirical interventional Shapley calculation remains tractable. Repeat the fixed training/validation/test partition, original seeds and original audited records. Do not substitute the expanded-model AUC into these results.
2. Controlled decision-to-notice benchmark: use these HELOC records and measured attribution outputs inside an explicitly constructed research decision policy. Institutional policies, notices and errors in this track are simulated. Regulatory cases motivate failure patterns; they are not reconstructed from confidential lender records.

## Reference and fidelity experiment
For the same 40 audited records, calculate exact empirical interventional Shapley values using (a) 24 training records drawn from the training population and (b) 24 records with Bad-class scores in [0.45, 0.50), immediately on the research acceptance side of the 0.50 cutoff. Use background seeds 101, 202 and 303 for both definitions. Report pool counts; if fewer than 24 records satisfy the cutoff band, stop rather than silently widen it. No test/validation records enter the reference pools.
Compare population vs near-cutoff reference using matched seeds; compare resampling within each reference definition. Measure reason-set turnover, retention and first-reason change using the actual list length, signed contributions, and at most four positive feature reasons. Aggregate comparisons within records before averaging across records. Bootstrap whole records 1,000 times with seed 2026. This selected rejection sample is not representative of US borrowers.
For the custom LIME-style surrogate, fit with 1,200 samples at seeds 0–4. Evaluate weighted R² and weighted mean absolute prediction error on an independently sampled 1,200-record neighborhood at seed+10,000, using the same interpretable representation and kernel. Also report absolute prediction error at the original applicant. These neighborhoods may break feature dependence. R² is approximation fit under this sampling scheme, not a fraction of correct reasons. Do not call custom output official LIME.

## Benchmark partition and scenarios
Partition the 40 original audited records into 20 development and 20 evaluation records using seed 20261016. All scenarios derived from a record remain in its partition. Store the partition before generating results. Thresholds and review logic are frozen before evaluation. The evaluator must not expose scenario labels or split membership to the audit function.

Three defect families:
- Mapping: a principal feature is translated to the wrong concept or unsupported directional wording. Development and evaluation use different replacement descriptions.
- Decision coverage: the research policy first applies an eligibility gate and stops if it fails; a notice explains an unused model score instead of the gate. A failed gate is constructed as an independent research flag, not inferred from HELOC.
- Provenance: explanation/model or mapping versions do not match the decision record being explained.

Four correct controls: correct model-driven notice; approved paraphrase of a correct reason; correct eligibility-gate notice; archived historical decision using its matching historical artifacts even when a newer model exists. A ninth scenario intentionally withholds the decision trace; the correct review disposition is insufficient evidence, not a confirmed wrong notice.

Nine scenarios per record: four controls; two mapping defects; one decision-coverage defect; one provenance defect; one missing-evidence case. Evaluation therefore contains 80 known-defective notices, 80 correct notices and 20 insufficient-evidence cases. These are constructed equal-frequency scenarios, not deployment prevalence. Do not treat 180 scenarios as independent borrowers.

## Comparators
Stability-only: flag if the original five custom-surrogate runs produce a differing top-four feature reason set in more than 20% of their ten pairwise comparisons. This illustrative screening threshold is not a legal standard. Apply the same stability result to every downstream notice for that record, since the model explanations are held fixed. Report a supplementary 0–100% threshold sweep; do not tune the primary threshold to evaluation outcomes.
Evidence review: inspect the candidate notice against independently retained decision trace, reason-mapping catalog and version identifiers. Check declared source features and category wording, signed support for model reasons, completeness of active policy reasons and decision/artifact version agreement. Return findings with evidence locations, or insufficient evidence when the trace/catalog is absent. Never read injected-defect labels.

## Outcomes and uncertainty
For evaluation records only, report confirmed-defect detection rate per family, overall sensitivity, false-alarm rate on correct controls, and insufficient-evidence disposition. A flagged correct notice is a false alarm. Report all method abstentions. Provide record-cluster bootstrap intervals and per-record paired comparisons, not binomial intervals assuming independent scenario rows. Include counts and original case IDs.

## Hypotheses and limitations
H1: downstream mapping, coverage and version errors can remain unchanged despite repeatable attribution outputs.
H2: structured evidence checks detect more constructed downstream errors than the repeatability-only screen while avoiding some unnecessary flags.
H3: reference definition affects feature reasons even when model and applicant are unchanged. No direction or effect size is assumed.
The structured audit has access to more evidence than the stability screen: this is an incremental-evidence comparison, not an equal-information algorithm contest. Same-author defect construction and deterministic review rules create favorable conditions; held-out records and variants do not establish robustness to new defect families. A successful result validates consistency with the research contracts, not legal principal-reason ground truth. Missing, false or collusively altered source evidence can defeat reconstruction checks. No actual lender notices, consumer comprehension, protected-group effects or feasible recourse are evaluated.

## Artifact and communication
Publish protocol hash, partition, code, model settings, explanation methods, scenario truth labels separately from audit inputs, findings and reproducible summary. The landing page contains title, why this matters and proposed use. Technical counts and method identities belong with results and research design. Poster reports completed results only and identifies the controlled nature of the benchmark beside its principal chart.
