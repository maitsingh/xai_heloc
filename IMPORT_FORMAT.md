# Import your own explanation evidence

Use case: a lender's consumer-compliance or model-risk reviewer has received explanation outputs from a model developer or vendor and wants to compare how a fixed prediction is attributed under different comparison populations or samples.

The browser compares the supplied attributions and generates a source-linked evidence brief. It does not execute an unknown model or infer that its outputs are authentic. It does not compare wording against a supposed approved list and does not generate an overall compliance verdict.

Open **Import explanation results** in the site. Download its example JSON, or export using `src/evidence_export.py`. Files are processed in memory in the browser; no backend or network request processes them. Maximum file size 5 MB, 500 application examples, 300 inputs, and 20 explanations per application.

Required structure (schematic—not empirical research results):

```json
{
  "schema_version": "credit-explanation-evidence/v1",
  "title": "Example vendor evidence export",
  "model": {
    "id": "model-version-identifier",
    "output": "the defined adverse repayment outcome",
    "score_scale": "probability"
  },
  "features": [
    {"id": "account_age", "label": "Average account age", "group": "Credit history"},
    {"id": "balance", "label": "Revolving balance", "group": "Balances"}
  ],
  "applications": [{
    "id": "example-1",
    "score": 0.60,
    "shapley": [
      {"id": "A", "reference": "Comparison A", "baseline": 0.40,
       "values": {"account_age": 0.15, "balance": 0.05}},
      {"id": "B", "reference": "Comparison B", "baseline": 0.45,
       "values": {"account_age": 0.05, "balance": 0.10}}
    ]
  }]
}
```

Every explanation must refer to the same input record, model version, output class and prediction scale. The format holds one prediction per application; the reviewer must verify that this identity is genuine. Supply **all** input contributions, including negative and zero contributions, not only a top-four list. Baseline plus contributions should reconstruct the supplied score. Residual discrepancies are surfaced in the finding rather than hidden.

Only probability-scale model outputs are supported. Do not use log-odds or raw-margin SHAP values against a probability prediction; export a probability-output explanation or adapt the analysis outside this tool. A probability-scale score is a model estimate: interpretation as an empirically reliable default rate requires calibration and population evidence.

Optional explanation fields: `detail` describes the sample and `method` identifies the implementation. Optional feature field `group` specifies a research or institution-defined grouping. Signed contributions are summed before selecting positive grouped contributions. The grouping is not assumed to be approved for notice use.

An application may also contain `local_approximations`, an array of:

```json
{
  "id": "attempt-1",
  "method": "Official LIME or accurately named alternative",
  "description": "Representation, neighborhood, weighting and evaluation design",
  "coefficients": {"account_age": 0.1, "balance": 0.05},
  "prediction_at_application": 0.59,
  "fidelity": {"r2": 0.7, "mae": 0.03, "evaluation": "independent_generated"}
}
```

This is a schematic example. `evaluation` must be `independent_generated`, `fitting_only`, or `other`. R² and MAE are supplied measurements; the browser does not recompute them from evaluation data or authenticate their origin. The original report and separately held evaluation samples should be requested when needed. Omit local approximations if none were measured; the product explicitly identifies the evidence gap.

The paired external-score experiment is available only for the measured HELOC demonstration. An imported Shapley export is not silently treated as a paired model experiment.
