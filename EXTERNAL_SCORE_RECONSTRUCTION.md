# Can an inferred scoring model substantiate the original reasons?

## Design and provenance

Exploratory extension specified 18 October 2026 after a feasibility run. The pilot had already shown external-score test MAE about 3.85 points for standardized Ridge and 3.24 for histogram gradient boosting using the eight existing credit inputs. No claim of preregistration or independent confirmation is made. No reviewer study is planned for this submission. Record 8193 was selected after inspection as a detailed-factor-change example with close prediction agreement; all forty audited records remain selectable.

The existing nine-input Random Forest is held fixed. Its observed `ExternalRiskEstimate` input is replaced with a prediction from either of two approximations trained only on the original training partition: standardized Ridge(alpha=10) or HistGradientBoostingRegressor(max_iter=150,max_leaf_nodes=15,l2_regularization=5,random_state=2026). Approximation fitting excludes records whose external score is a negative status code. Neither approximation is an authenticated reconstruction of the original scoring system.

The raw external score is the regression target; repayment class is not the approximation target. The approximation encoder is fitted on eligible training records only. Estimates are clipped to the eligible training target's observed min/max; the clipping rule is reported. Both the lender-side predictor and the two approximation models are deterministic for this run. The test partition had already been used in prior studies and in the feasibility run: estimates are exploratory and must not be described as pristine confirmatory performance.

## Questions and measurements

1. How closely can available inputs predict the observed external score? Report test MAE, R-squared and error quantiles for both approximations.
2. How closely do the reconstructed combined systems match the original nine-input model? Report mean absolute probability difference on all eligible test records and per audited record. No observed approval/denial or lender policy is inferred.
3. Do reconstructed combined systems assign the same leading adverse contributions? For the forty previously selected records with observed external scores, compute exact empirical interventional Shapley attributions for both eight-input reconstructed pipelines against the identical 24 eligible training reference records. Recalculate the original nine-input model’s attributions against those same record IDs, using their observed external scores. Its model and predictions remain unchanged; these new reference-conditioned contributions are distinct from the earlier experiment’s configuration.
4. Compare top-four positive-contribution sets, their order and credit-concept grouping. Report different memberships separately from changed ordering and differences between credit concepts. Do not label any of these legal violations or consumer harm.
5. Report joint output-agreement and explanation-agreement results at several descriptive probability-difference bands (0.5, 1, 2 and 5 percentage points). These are sensitivity bands, not adequacy thresholds. Also report differences from the original model so two equally inaccurate reconstructions are not mistaken for good approximations.

The constructed combined systems use the original eight raw inputs, each estimated score and the frozen original nine-input model. Other raw inputs remain directly available to that model. Therefore direct and score-mediated paths can overlap. Their explanations are of these combined systems, not estimates of the provider's true internal feature contributions. Correlated-feature replacements and special missingness states can create implausible Shapley combinations.

## Governance response

Assess four claims separately: the original lender-side model's reliance on an observed score; predictive accuracy of an inferred score model; the inferred model's attributions; and identification of factors actually used inside the original score. Empirical predictive fit supports the second claim, not automatically the fourth. Agreement between inferred models does not authenticate the original process; disagreement can show that this reconstruction strategy has not resolved explanatory uncertainty.

The outcome is a documented assessment of what each evidence source supports and a specific request for score-provider documentation, decision-linked reason codes or validation access where the proposed use requires those facts. It is not an automated notice certification or a blanket restriction on using external scores. US Regulation B reason duties, FCRA score disclosures, EU AI Act institutional transparency and New York materials are separate scope analyses.

## Evaluation and boundaries

Evaluate actual numerical accuracy, decomposition reconstruction and cross-approximation differences. Do not inflate software checks into evidence of reviewer effectiveness. The study cannot establish what the original external-score system actually used, real notice accuracy, group fairness, legal compliance or applicant comprehension. A poor reconstruction is still a reportable result. No result is required to show high predictive agreement with explanation disagreement.
