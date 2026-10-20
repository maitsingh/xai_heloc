Live workbench

[Open the Reason Integrity Workbench]: 

# From Risk Scores to Reasons

**A reason-integrity workbench for credit decisions that rely on external scores**

When a creditor gives an applicant a reason for an adverse decision, the question is not only whether the model can be explained. The creditor also needs evidence that the stated reason is tied to the decision process that actually ran.

That becomes harder when the lending model depends on an external score whose internal calculation is unavailable.

This project studies that problem using the public FICO HELOC dataset and turns the results into an interactive review workbench for compliance, model-risk, and validation teams.

## Live project

- **Workbench:** [Open the live site][(https://maitsingh.github.io/xai_heloc/)
- **Reproduce the analysis:** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/maitsingh/xai_heloc/blob/main/From_Risk_Scores_to_Reasons_Colab.ipynb)
- **Policy implications:** [Read the policy note](POLICY_RECOMMENDATIONS.md)

---

## The question

If a lender can estimate an external credit score closely enough to reproduce a downstream prediction, does that mean it has also recovered the original provider's reasons?

This project tests that assumption.

The broader governance question is:

> **Can a consumer-facing reason be traced to the model, mapping, version, and records that actually support it?**

---

## Why this matters

Credit explanations can cross several systems and organizations:

**consumer-facing reason ← reason mapping ← lender model ← external score ← score provider**

Each step is an evidence handoff.

A downstream explanation can show how an external score affected the lender's model. It does not automatically reveal how the external score itself was produced.

That distinction matters for:

- **Consumers**, who may rely on stated reasons to identify errors or challenge a decision.
- **Compliance teams and counsel**, who need to determine whether reasons accurately reflect the factors actually considered.
- **Model validators and model-risk teams**, who may need to assess third-party components they cannot fully inspect.
- **Supervisors**, who need evidence that reason-selection methods have actually been validated.

---

## What I built

The project has two parts:

1. **An empirical stress test**
   - Train a Random Forest to predict serious late payment from eight credit attributes plus an externally supplied risk score.
   - Estimate that score in two different ways:
     - Ridge regression
     - Histogram gradient boosting
   - Substitute each estimated score into the same frozen Random Forest.
   - Compare downstream predictions and explanation outputs.
   - Use exact empirical interventional Shapley decompositions and repeated LIME-style local approximations.

2. **A review workbench**
   - Inspect a historical record.
   - Compare detailed factors and broader grouped topics.
   - Review explanation fidelity and consistency.
   - Identify what evidence is measured, inferred, or unavailable.
   - Export a review note listing unresolved evidence and records to request.

---

## Headline finding

For the featured example:

- Original repayment-risk prediction: **95.47%**
- Ridge-score reconstruction: **95.34%**
- Boosted-tree reconstruction: **95.47%**

The predictions are nearly identical, but the detailed explanation sets differ.

Across the 40 selected records:

- **12** had all three predictions within **1 percentage point**
- **4 of those 12** had different leading individual-factor sets
- **0 of those 12** had different leading broader-topic sets

So broad explanation categories can remain stable even when the underlying detailed factors change.

### Main takeaway

> **Prediction agreement does not establish explanation provenance.**

A reconstructed score can be useful for sensitivity analysis, but it does not authenticate the original provider's internal reasons.

---

## Policy implication

If an external score materially contributes to a credit decision, a lender should distinguish between:

- what its own model establishes,
- what is inferred from a reconstructed score,
- and what has been supported by provider-linked evidence.

A reconstructed score should not be treated as a substitute for evidence about the provider's actual reason-generation process.

A review process should therefore preserve the provenance of consumer-facing reasons and identify when additional provider or lender records are required.

---

## Rules → claims → tests

The governance sources in this project are treated as review questions rather than background material.

| Source / practice | Review claim | Protocol test | Evidence still needed |
|---|---|---|---|
| **ECOA / Regulation B** | Does the proposed reason trace to the actual decision evidence? | Decision fidelity + mapping integrity | Actual decision path, scored factors, mapping/version, notice wording |
| **CFPB supervisory finding** | Has the reason-selection process been tested rather than assumed? | Fidelity + reason consistency | Validation design, cases, exceptions, retained results |
| **Upstart methodology** | What changes when detailed SHAP features are grouped into broader reason categories? | Reason consistency + mapping integrity | Grouping rules, directionality checks, production mapping |
| **Third-party model risk** | Is the explanation evidence from the original provider or from a reconstruction? | Provenance | Provider version, inputs, reason codes, validation access |
| **EU AI Act comparison** | Could the explanation process be reconstructed and reviewed? | Auditability | Versioned records, system information, oversight trail |
| **State / product rules** | Which lending and notice requirements apply to the transaction? | Applicability overlay | Charter, product, collateral, terms, jurisdiction, consumer-report use |

---

## Five-test validation protocol

The workbench does not assign one generic "explanation quality" score. Each test answers a different question.

### 1. Decision fidelity

Does the explanation represent the model being reviewed?

For the featured case, the exact Shapley decomposition closes numerically, and the repeated local surrogate provides a separate local-fidelity check.

### 2. Reason consistency

Do leading factors remain the same across reasonable reconstruction or explanation choices?

For record 8193, the individual-factor sets differ between the Ridge and boosted reconstructions, while the broader-topic sets match.

### 3. Mapping integrity

Can a consumer-facing reason be traced to the features and mapping logic that produced it?

This cannot be fully tested with HELOC because the data do not include an actual adverse-action notice or a production feature-to-reason mapping.

### 4. Provenance

Does the evidence come from the original external score provider or from an inferred substitute?

The external score is observed, but its original provider mechanism is unavailable. The reconstructions therefore explain their own substitute mechanisms, not the original score.

### 5. Auditability

Could another reviewer reconstruct how the explanation was produced?

The research artifact retains the record, model outputs, explanation settings, reference population, and comparison results. A production review would also need lender decision rules, overrides, notice delivery records, mapping versions, and provider documentation.

---

## What this project can establish

The project can measure:

- the effect of the external score on the downstream Random Forest,
- the accuracy of the score reconstructions,
- the change in downstream predictions after substitution,
- Shapley contributions in the research systems,
- local approximation fidelity,
- and explanation agreement across reconstructed systems.

## What it cannot establish

The project does **not** establish:

- the original external score's internal formula,
- the actual factors used by the original score provider,
- the accuracy of a real adverse-action notice,
- whether a lender complied with a specific legal requirement,
- protected-group fairness,
- consumer understanding,
- or reviewer effectiveness.

---

## Methods

### Data

Public FICO HELOC data with credit attributes, an external risk estimate, and a repayment outcome.

The research model predicts the dataset's serious-late-payment outcome, not approval or denial.

### Models

- Random Forest downstream model
- Ridge regression external-score estimator
- Histogram gradient boosting external-score estimator

The downstream Random Forest is held fixed while the supplied external score is replaced with each estimate.

### Explanations

- Exact empirical interventional Shapley decomposition
- Custom LIME-style weighted local regression
- Individual-feature and grouped-topic comparisons

The same reference-record identities are used for the Shapley calculations across systems.

---

## Reproduce the analysis

### Colab

[Open the reproduction notebook in Colab]((https://colab.research.google.com/github/maitsingh/xai_heloc/blob/main/From_Risk_Scores_to_Reasons_Colab.ipynb))
