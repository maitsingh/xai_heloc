# GitHub / GitHub Pages setup

This repository is ready to push as-is.

## Create the repository

Suggested repository name: `from-risk-scores-to-reasons`

```bash
git init
git add .
git commit -m "Final project: From Risk Scores to Reasons"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/from-risk-scores-to-reasons.git
git push -u origin main
```

## Publish the workbench with GitHub Pages

In the repository on GitHub: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / root**.

The root `index.html` redirects to `site/`, which is a fully static workbench. No backend or secrets are required.

## Colab link after publishing

Once the repository is public, the notebook can be opened at:

`https://colab.research.google.com/github/YOUR-USERNAME/from-risk-scores-to-reasons/blob/main/notebooks/03_reproduce_workbench.ipynb`

Replace `YOUR-USERNAME` with the GitHub account name.
