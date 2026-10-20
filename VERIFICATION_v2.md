> Historical version: this document describes an earlier interface or verification run. See README.md and DECISION_RECONSTRUCTION_PROTOCOL.md for the current project.

# Verification and release status

## Completed
- Thirteen analytical tests: status encoding, exact Shapley efficiency, signed grouping, empty-list comparisons, record partitions, matching historical artifacts, missing-evidence abstention, terminating-rule coverage, reference reconstruction and independent-neighborhood anchor handling.
- Browser/Python checker parity on all 360 primary scenarios and 40 supplementary challenges. Truth labels are not passed to the review function.
- Interaction smoke checks for all nine notice variants, six sections, editable-wording handlers, reference/method selection, challenge cases, saved reviewer notes and the threshold sweep. These use a simulated DOM, not a real browser.
- Numerical browser reconstruction of all 40 retained predictions from 100-tree model arrays and original encoding; maximum observed error zero.
- Every one of 240 reference explanations reconstructs its unchanged prediction to numerical precision.
- The refitted surrogate coefficients match the earlier pilot. Independent evaluation does not force the original fitting anchor into its sample; the original-point error is reported separately.
- Portable notebook Python cells parse. The notebook stages its own sources and protocol and excludes raw CSV from exports.
- Poster is a one-page 36 × 24 inch PDF, rendered to PNG and visually inspected. Text, sources and measured values are embedded in the PDF.

## Outstanding
- Official SHAP/LIME library execution: dependencies unavailable in this session. Colab reproduction and optional official figure generation are supplied. The site automatically exposes official views for matching cases if an official output file is added and its scores agree.
- Actual browser visual and mobile-device testing: no browser executable was available. Desktop/mobile design concepts were produced; the implemented site uses responsive layout and horizontally scrollable detailed plots, but simulated-DOM tests cannot establish rendered visual quality.
- GitHub merge/deployment: remote publishing unavailable. The source includes a Pages workflow; no push or deployment is claimed.
- Original FICO data dictionary and redistribution terms: source-access verification remains incomplete. A supplied-file checksum is recorded; no raw CSV is redistributed. Public-record explanations/model artifacts are included for reproducibility.
- Independent domain review, independently authored challenge cases, consumer comprehension and actual lender validation remain future evaluation.

## Interpretation
Primary contract-detection results reflect favorable constructed conditions and access to extra evidence. Held-out records do not establish performance on unknown failure families. The separate challenges deliberately expose wording and trusted-catalog failure modes; they were introduced after primary results without modifying the checker.
