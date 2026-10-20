> Historical version: this document describes an earlier interface or verification run. See README.md and DECISION_RECONSTRUCTION_PROTOCOL.md for the current project.

# Verification: accessible review and external-score extension

- 17 Python analytical tests pass, including all 80 Shapley reconstructions, 40 unchanged original-model contributions, unfiltered pairing, and positive-contribution summary counts.
- Python and browser JavaScript evidence checkers agree on 360 primary examples and 40 follow-up challenges.
- JavaScript minimal-DOM checks exercise guided navigation through four questions, all nine notice types, selectable reasons, five local-approximation attempts, comparison-group/grouping controls, challenge failures, saved requests, all 40 external-score comparisons and primary-model numerical reconstruction.
- Site JavaScript passes syntax checking. All Colab code cells and the extracted Python script parse. The notebook stages the external-score source and runs it after the original studies and before the site build.
- The complete new external-score experiment ran locally. Baseline eight-input predictions and Shapley values match retained original results within 1e-10. Sampling, model settings and measured per-record outputs are retained.
- Raw CSV and cache/archive directories are excluded from distribution ZIPs. The site-only ZIP has index.html, app.js, review.js and data.js at its root.
- A browser executable is not installed; desktop/mobile visual rendering and real-browser keyboard QA were not performed. Minimal-DOM tests do not replace them. The site uses responsive columns, native controls, visible focus, direct labels and stacked mobile evidence views.
- Official SHAP/LIME packages were not available locally. The optional Colab path remains available and clearly distinguished. The shipped exact Shapley and custom LIME-style outputs are measured.
- The previously supplied poster represents the earlier study. It is not silently updated to claim the new experiment was included.
