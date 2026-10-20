# External-score extension: measured results

The same Random Forest settings were applied to the same train/test partitions, with eight original credit-history inputs and then with ExternalRiskEstimate added. All 40 original audit applications were retained, including changed research outcomes. This exploratory design was recorded after overlapping earlier pilot results were known. See EXTERNAL_SCORE_ADDENDUM.md.

- Full-test ROC AUC without external score: 0.7708787536.
- Full-test ROC AUC with external score: 0.7821133278.
- Paired AUC difference: 0.0112345742; application-bootstrap 95% interval [0.0041424379, 0.0182184963], 1,000 resamples.
- Outcomes at the research threshold of 0.50 differ for 134/1,975 test applications.
- Among all 40 original audit applications, 8 research outcomes change.
- The external score is among up to four positive Shapley contributors for 33/40 applications; it has the largest absolute contribution for 28/40. These are different measures, not interchangeable definitions of dominance.
- Exact empirical interventional Shapley explanations reconstruct both models' scores for all 80 application-model pairs. All eight-input scores and contributions reproduce the earlier audit numerically.
- Ten test-set permutations per raw input assess model reliance through mean AUC loss. Dependence among features limits causal interpretation.
- Five custom LIME-style local fits per application-model pair have independent-neighborhood fidelity measurements. The original eight-input fidelity is reused; nine-input fits are newly measured.

The available snapshot contains external-score values, but no authenticated upstream model, score calculation or upstream reasons. Reconstructing the lender-side model does not reconstruct that scoring system. Removing the score trains a different model; neither explanation is an explanation of the other model's decision.

The selected 40 applications do not estimate prevalence across US borrowers. No consumer comprehension or institutional liability was measured.
