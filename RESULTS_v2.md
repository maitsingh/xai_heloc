# Measured results and interpretation

The new protocol was frozen before these runs, after the earlier pilot and classifier comparison were known. It is an internal prospective protocol, not an external preregistration. All scenario policies, notices and defects are constructed.

## Primary notice benchmark

| Method | Scenario family | Flagged / scenarios | Rate | 95% record-bootstrap interval |
|---|---|---:|---:|---:|
| Repeatability screen | mapping | 24 / 40 | 0.600 | 0.400–0.800 |
| Repeatability screen | coverage | 12 / 20 | 0.600 | 0.400–0.800 |
| Repeatability screen | provenance | 12 / 20 | 0.600 | 0.400–0.800 |
| Repeatability screen | all_defects | 48 / 80 | 0.600 | 0.400–0.800 |
| Repeatability screen | correct | 48 / 80 | 0.600 | 0.400–0.800 |
| Structured evidence review | mapping | 40 / 40 | 1.000 | 1.000–1.000 |
| Structured evidence review | coverage | 20 / 20 | 1.000 | 1.000–1.000 |
| Structured evidence review | provenance | 20 / 20 | 1.000 | 1.000–1.000 |
| Structured evidence review | all_defects | 80 / 80 | 1.000 | 1.000–1.000 |
| Structured evidence review | correct | 0 / 80 | 0.000 | 0.000–0.000 |

Evaluation contains 20 held-out records; each contributes four defect variants, four correct controls and one missing-trace case. The additional 20 development records are excluded. All 20 missing traces produce an insufficient-evidence disposition. Bootstrap resamples the 20 records rather than treating 180 scenarios as independent. Degenerate zero/one intervals reflect identical observed outcomes; they do not prove future certainty.

The repeatability flag is identical across notice variants for a record by construction. Equal detection and false-alarm rates are therefore a property of the design, not a surprising statistical discovery. The evidence checker receives additional decision traces and catalogs; its favorable primary detection tests consistency against these supplied contracts. It is not a superior equal-information estimator of legal correctness.

## Deliberate post-primary challenges

All 20 stipulated-correct unlisted paraphrases are flagged. None of 20 wrong reasons entered consistently in the trusted mapping catalog are detected. These same-author challenge examples were added after primary results and targeted known checker limitations; no primary thresholds or rules changed. They show exact-catalog false alarms and the dependence on accurate source evidence.

## Reference sensitivity

| Comparison | Reason-set turnover | 95% record-bootstrap interval | Retention | First reason changed |
|---|---:|---:|---:|---:|
| population_vs_near_cutoff | 0.5333 | 0.4250–0.6500 | 0.8597 | 0.1750 |
| population | 0.5750 | 0.4667–0.6752 | 0.8306 | 0.0500 |
| near_cutoff | 0.4583 | 0.3417–0.5750 | 0.8993 | 0.2667 |

The model and applicant are held fixed. Each of 40 selected records contributes three comparisons per condition; comparisons are averaged within records. Each reference contains 24 rows. The population reference pool has 5,922 training records; the near-cutoff pool has 273 records with model scores in [0.45, 0.50). These are research acceptance-side records, not observed approvals.

Resampling variability is comparable to differences between reference definitions. With only three seeds and small background samples, the experiment does not establish that the policy choice dominates sampling effects or identify a legally preferred reference. Exact coalition enumeration removes coalition-estimation error, not uncertainty from the empirical reference distribution.

## Independent-neighborhood local fit

| Statistic | Median | Minimum | Maximum |
|---|---:|---:|---:|
| fit_r2 | 0.565260 | 0.074959 | 0.781446 |
| heldout_r2 | 0.552867 | 0.068999 | 0.769229 |
| heldout_mae | 0.051714 | 0.020510 | 0.108963 |
| point_error | 0.008499 | 0.000050 | 0.044552 |

The 200 fits are five seeds for each of 40 records. Fit and evaluation neighborhoods each contain 1,200 points, generated with different seeds using the same sampling process. They may contain implausible feature combinations. R² is not the fraction of correct reasons and these custom-surrogate results do not characterize the official LIME package.

## Models and reconstruction

The audited eight-feature Random Forest has test AUC 0.770879. The separate validation-selected 22-feature model has test AUC 0.784694; its explanations were not substituted. The browser evaluates the retained 100 trees, with the original medians and separate special-state indicators. All 40 original scores reconstruct within numerical precision. This is a numerical consistency check, not authentication of historical institutional artifacts.

## Contribution and boundary

The contribution is a reproducible decision-to-notice workbench and controlled comparison of the evidence supplied to a review, together with an empirical reference/fidelity experiment. Known-defect evaluation, grouping and explanation sensitivity are established ideas. No actual lender notices, new defect-family generalization, consumer comprehension, fair-lending outcomes or feasible recourse were evaluated. Official SHAP/LIME runs remain pending; their portable notebook and plots are supplied.
