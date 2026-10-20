# Colab reproduction

Use `notebooks/03_reproduce_workbench.ipynb`. The notebook is intentionally portable: it stages the repository files inside the Colab runtime, then asks you to upload `heloc_dataset_v1.csv`.

The notebook does **not** download or redistribute the raw HELOC dataset. Verify that you are authorized to use the file and that its schema matches the project expectations.

The final verification cell checks the project’s headline 1.0 percentage-point agreement result: 12 close-prediction records, 4 with different leading detailed-factor sets, and 0 with different grouped-topic sets.
