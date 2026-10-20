> Historical version: this document describes an earlier interface or verification run. See README.md and DECISION_RECONSTRUCTION_PROTOCOL.md for the current project.

# Accessible review language

Primary audience: consumer-compliance teams reviewing automated credit decisions. Secondary audiences: model-risk reviewers, students and hiring reviewers exploring a guided example.

The four questions are: What was the applicant told? What determined the decision? How much confidence should we place in the explanation? What should the reviewer do next?

Technical labels belong with definitions and detailed evidence. Main labels describe the user's question.

| Technical term | Main-interface explanation |
|---|---|
| Dataset record | Example application: credit-history information and a repayment outcome from HELOC |
| Classifier | Credit-risk prediction model |
| Cutoff | Research score threshold that separates acceptance and denial |
| Reference/background sample | Applications used as the comparison group |
| Random seed | Technical setting controlling a reproducible sample or repeated attempt |
| Signed Shapley contribution | How much an input raises or lowers predicted risk relative to the comparison group |
| Grouping | Which related credit factors are combined into a broader reason category |
| Local surrogate | Simpler explanation fitted around one application |
| Fidelity / local R² | How closely that explanation follows the prediction model on a defined nearby test |
| Reason-set turnover | How often at least one factor enters or leaves a reason list |
| Controlled benchmark | Test using deliberately introduced notice or record errors |
| Held-out records | Applications reserved for final evaluation |
| Controls | Examples without the errors being tested |
| Decision trace | Recorded conditions checked and what determined the outcome |
| Version provenance | Which model and explanation settings were used at the decision date |
| Unlisted paraphrase | Accurate wording absent from the approved list |
| Corrupted catalog | Incorrect wording also entered into the approved list |

Method names remain explicit. The shipped calculations use exact empirical interventional Shapley values and a custom LIME-style approximation. Optional official SHAP/LIME outputs acquire their own labels after execution. The site never presents the custom approximation as the official package.
