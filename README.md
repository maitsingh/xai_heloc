# Explanation Assurance Workbench

How mapping feature explanations into broader reason-categories changes apparent consistency. Home Equity Line of Credit information as released by FICA is a familiar benchmark.

## Current evidence
A real reference pilot ran on the uploaded raw HELOC CSV. It uses exact empirical interventional Shapley and a disclosed custom LIME-style local surrogate.  
 
## Run the pilot
Install `requirements-reference.txt`. Obtain the raw FICO HELOC CSV separately.

```
python src/audit.py --data data/heloc_dataset_v1.csv --out results/reference --cases 40 --repeats 5
python -m unittest discover -s tests -v
```

The expected supplied CSV SHA-256 is `e5a914f742ad7f8472c5417902ec06b321ebc5de1d68ec13f136d62c87a7fbf3`.

## Official SHAP/LIME run in Colab
Open `notebooks/02_mapping_audit.ipynb`; it embeds the pipeline so you do not need GitHub connectivity. Install the dependencies in that notebook, upload the CSV, run with `--official`, and download results. KernelSHAP calls the full preprocessing/prediction wrapper on raw feature blocks; this preserves the special-state indicators within each feature attribution. LIME uses the official package. Review its synthetic neighborhood limitations. The model is Random Forest, not XGBoost.

Enable Pages from `/docs`, copying `site/index.html` and `site/results.js` into that folder without overwriting existing docs; alternatively configure a Pages workflow. Refresh the website export after official runs; never replace its reference-pilot label without changing the evidence.

## What is tested
Two models with eight selected features, adding ExternalRiskEstimate in the second. Primary sample: 40 held-out simulated rejections. Five surrogate seeds create ten within-applicant comparisons. Measurement sensitivity changes only the two balance ratios by +/-1 point, preserves special states, and records all attempted changes. These changes are not validated recourse or a claim about actual borrower behavior. MaxDelq categorical codes are excluded from the reduced feature set instead of being silently treated as ordinal.

## Important interpretations
- Four is a reporting convention, not a legal mandate; fewer positive reasons remain shorter lists.
- Exact Shapley explains deviation from its background, not all reasons for a real creditor decision.
- Local-surrogate coefficients explain local conditions; they are not interchangeable with Shapley values.
- Grouping sums signed feature contributions BEFORE selecting positive groups. It is a postprocessing taxonomy, not grouped coalition Shapley.
- Fewer categories and changed list lengths can mechanically improve agreement. Inspect both levels and member evidence; no superiority claim follows.
- Duplicate predictor patterns remain in one split. All-no-bureau records are quarantined.
- No-record exclusion limits coverage for thin-file applicants and requires its own deployment control. 

## Governance and legal scope
Hypothetical US consumer creditor and NC-resident HELOC application. Federal Reg B reasons/process, conditional FCRA, and NC G.S. 75-1.1 are mapped to evidence; lender/product/preemption facts are unresolved. Legal coverage is preliminary, not exhaustive. Withdrawn CFPB Circular 2022-03 is historical only.  

## Contents
- src/audit.py: experiment implementation
- tests/: analytical and boundary checks
- results/reference/: measured outputs, comparisons, attempt log, split IDs and manifest
- site/: static workbench
- docs/: protocol, results interpretation, source/legal register and prior-work distinctions
- notebooks/: portable Colab pipeline

## Governance-facing revision
Rebuild with `python src/build_governance_site.py`. The added `docs/governance_use.md` explains the policy use case, stages, technical vocabulary and sources. Evidence & follow-up computes findings from the selected model, records reviewer-reported documents, and exports a review record.  
