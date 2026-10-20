# Five-minute demonstration

## 0:00–0:45 · Problem and research question

Open **About**, then briefly show **Rules & real cases**.

A credit denial gives an applicant reasons for the decision. A compliance reviewer needs evidence that those reasons describe the factors actually considered. The CFPB's Winter 2025 findings give a concrete motivation: examiners identified AI/ML lending reason-selection methods that had not been adequately validated.

My project examines one complication: a lending model can use a credit-risk score calculated by another system. Explaining how the lending model uses that number does not tell us how the number itself was calculated. I tested whether estimating the score from other credit information helps resolve that uncertainty.

## 0:45–1:35 · What the model predicts

Open **Inspect a prediction**, using the default record.

HELOC means home equity line of credit: borrowing against equity in a home. FICO's historical dataset contains credit information and repayment outcomes. It does not contain actual denial notices or the formula behind its external score.

I trained a Random Forest to predict the dataset's serious-late-payment outcome: at least 90 days overdue or worse within 24 months. The supplied score is 58 for this record. That is a score in the dataset, not a 58% probability. The Random Forest separately estimates a 95.47% probability for this historical record. This is a research-model output, not an actual lender's refusal or a verified forecast for a current applicant.

The Shapley chart shows the external score's contribution relative to 24 reference records. It explains a dependency in my model; it does not explain the provider's scoring process.

## 1:35–2:40 · Compare two estimated-score systems

Open **Compare explanations**. Show individual factors, then grouped factors.

I trained Ridge regression and gradient-boosted trees to estimate the supplied score using eight other credit attributes. Each estimate replaces the score in the same unchanged Random Forest. The charts explain those two combined research systems.

For the selected record, the repayment predictions differ by about 0.12 percentage points. Their leading individual-factor sets differ, but their broader topic sets match. Related measures can be grouped into topics when producing explanations; grouping here is explicitly a research choice, not a validated notice taxonomy.

Different models can legitimately have different explanations. I am examining how much information prediction agreement and topic agreement actually give a reviewer.

## 2:40–3:35 · Measured finding and its limits

Open **Findings** and demonstrate one alternative slider position.

Of 40 examined records, 12 have all three predictions within one percentage point of each other. Four of those 12 have different leading individual-factor sets. None have different leading broader-topic sets. The figure preserves both results. It does not imply that four applicants received inaccurate notices.

The approximations are also imperfect across the larger test sample. Their average repayment-prediction errors are 5.01 and 4.33 percentage points. The close default example is not typical of every record. The forty explanation records were selected earlier, and the analysis is exploratory.

## 3:35–4:30 · Governance contribution

Show the evidence assessment beneath the figure.

The workbench distinguishes what the evidence establishes from the proposed claim it cannot establish. It measures prediction error and contributions in the research systems. It cannot identify the factors actually used by the original provider.

A reviewer considering inferred factors as reasons for the original score should obtain provider reasons tied to that score, input definitions and validation evidence connecting the reasons to the scoring process. Reviewing an actual denial also requires the lender's decision rules and delivered notice. Agreement between approximations does not remove that evidence need.

## 4:30–5:00 · Supporting method, artifact and future work

Briefly show the LIME-style disclosure or the exported note; do not attempt both if time is short.

The supporting LIME-style check evaluates whether a simpler local explanation approximates the Random Forest. Even high local fidelity would leave the upstream scoring question unresolved.

The contribution is a reproducible experiment and interactive assessment of explanation evidence. Future work would obtain a scoring system with known internal factors and test which reconstruction or provider-evidence strategies resolve the uncertainty. This study has not evaluated actual notices or professional reviewer effectiveness.
