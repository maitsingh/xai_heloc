# Policy implications

## Recommendation

When a consumer-facing reason depends on a material external score, the creditor should be able to distinguish two things: what its own model shows, and what it can actually support about the score provider. A downstream explanation or reconstructed score does not, by itself, establish the provider's reasons.

This does not imply that external scores should be banned or that one explanation method should be required. The issue is narrower: the record supporting the notice can cross an organizational boundary, and the evidence has to cross that boundary too.

## What should change

1. **Keep a provenance record for external-score decisions.** Retain the external score and version, lender model/version, reason-selection logic, explanation settings/reference, reason-mapping version, and notice output associated with the decision under review.
2. **Mark inference as inference.** A downstream feature contribution can be measured for the model being explained. Factors inferred from a reconstruction of the external score should not be presented as the provider's factors unless provider-linked records support that claim.
3. **Validate the basis of the notice category, not just the category label.** In this experiment, broad topic sets can stay the same even when the leading detailed factors change. A stable label does not show that the detailed basis for the label is stable.
4. **Allow the review to stop at an evidence gap.** If a proprietary component prevents the reviewer from tracing the reason any further, the next step is to request records from the lender or provider. The workflow should not convert that gap into a more confident explanation.

## Why the external-score result matters

Among 12 selected historical records where all three downstream predictions were within one percentage point, 4 had different leading individual-factor sets and 0 had different leading broader-topic sets. The counts are descriptive and come from an exploratory sample.

The result shows why output agreement is not enough. Two substitute mechanisms can land on almost the same downstream prediction and the same broad topic while attributing that result to different detailed factors. That leaves the original provider's mechanism unresolved.

## Consumer-advocate questions

An external provider's opacity should not leave the applicant with a specific reason that the creditor cannot connect to the decision path actually used. For a disputed reason, useful questions include:

- Did the reason come from the lender's own model, the external score, or a later mapping step?
- If the external score mattered, did the lender receive provider-linked reasons or infer them internally?
- Which score/model and mapping versions were used for this decision?
- Can the institution reproduce the path from model evidence to the wording given to the applicant?

This project does not establish that any named lender failed these expectations, and it does not determine legal compliance for an actual transaction.

## Supervisory and counsel review

For a sampled adverse action, ask for the evidence behind the reason, not just the name of the XAI method. Relevant records may include the lender model/version, external score/version, feature or score contribution used in reason selection, the mapping into consumer-facing wording, validation of that mapping, and provider-linked evidence for any reason attributed to the external score.

## Next evaluation

A stronger follow-up study would use a controlled or real adverse-action pipeline where the decision path and reason mapping are known. That would make it possible to test whether reviewers using this protocol identify unsupported reasons more accurately and consistently.
