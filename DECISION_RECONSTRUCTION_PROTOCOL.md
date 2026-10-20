# Can the institution reconstruct the denial?

## Question and contribution

Can an institution reconstruct a credit decision from an explanation report alone? Which additional retained records make specified investigative tasks possible, and which questions remain unanswered?

This is a controlled evidence-removal experiment, specified on 18 October 2026 after the earlier explanation experiments. It is not preregistered. The contribution is a source-linked evidence specification, executable reconstruction procedure, and measured demonstration of the consequences of missing or mismatched records. It is not a new explanation algorithm.

## What is measured and what is constructed

Measured: the existing frozen eight-input Random Forest, forty selected historical HELOC records, its predictions, exact empirical interventional Shapley decompositions, custom LIME-style fits and independent-neighborhood fidelity. Original model outputs remain unchanged.

Constructed: an original lending policy that declines when the model's estimated probability of the dataset's `Bad` category is at least 0.50; a later policy using 0.65; decision timestamps, policy versions, and event records. These thresholds have no regulatory status and are not observed lender practices. Selection of twenty records just above 0.50 and twenty high estimates predates this experiment. Results describe this deliberately contrasting sample, not an estimate of lender error frequency.

HELOC means home equity line of credit, borrowing secured against equity in a home. Repayment labels are not lending decisions. No actual notices, appeals, human decisions, or protected-group attributes are supplied by this dataset.

## Procedure

For each of the forty records, evaluate seven retained-evidence packages:

1. Explanation report only: prediction and Shapley contributions, without executable model, original input snapshot or policy.
2. Original records: executable model and preprocessing, original input snapshot, original policy, logged prediction and decision, and explanation.
3. Original policy missing: original inputs and model remain.
4. Newer policy substituted: the original rule is replaced with the 0.65 rule.
5. Different model supplied: the retained artifact is substituted; its digest no longer matches the logged model identity.
6. Input snapshot altered: an account-age value is changed without changing the logged input identity.
7. Explanation altered: a contribution is increased by 0.10 without changing the recorded prediction or reference value.

The evaluator checks content digests against the original event record, actually reruns the frozen Python predictor for valid input/model combinations, applies a verified original policy, and checks whether reference plus contributions reconstructs the logged prediction. It abstains from original-decision reconstruction when identity cannot be verified. Hashes are assumed to have been retained in an independent, trustworthy event record; an attacker changing both records and digests defeats this check.

Separately, the experiment applies the later policy to the same measured predictions. This demonstrates how a changed institutional rule can alter outcomes without changing a prediction or its explanation. It is not an experiment in model fairness or explanation accuracy.

## Outcomes

Report counts for (a) arithmetic agreement of the explanation, (b) successful original-prediction reproduction, (c) successful original-decision reconstruction, and (d) detected identity or arithmetic inconsistencies. Keep missing evidence separate from contradictory evidence. No aggregate legal pass/fail score is produced.

The expected results are constructed from the manipulations and independently asserted in tests. Agreement with those expectations is an implementation check, not an external validation of the framework. No clinician, lender, regulator or user-study participant has validated the process. A subsequent reviewer study should measure task accuracy, unsupported conclusions, evidence requests and completion time against a chart-only baseline.

## What reconstruction cannot establish

Arithmetic agreement does not prove a Shapley attribution identifies legally sufficient principal reasons, causal drivers, valid counterfactuals or fair treatment. Successful replay does not establish data accuracy at source, lender-policy lawfulness, effective human oversight or notice delivery. Upstream score calculations remain unavailable even in the strongest package.

## Legal interpretation versus engineering proposal

Regulation B commentary 9(b)(2)-2, -4 and -7 connects reasons to actual scored/considered factors and the component responsible for denial. EU AI Act Articles 12, 13, 14, 26, 27 and 86 motivate distinct tasks concerning records, output interpretation, oversight, impact assessment and explanation. Our particular JSON fields and digest checks are proposed implementation choices, not statutory field specifications.

US and EU regimes are separate scope analyses. The US HELOC experiment does not become an EU-regulated deployment. New York S8115C is proposed lending legislation; NYDFS Circular Letter 7 (2024) concerns insurance. Neither is an additional applicable HELOC duty by default. Source status and timing are presented in the site.
