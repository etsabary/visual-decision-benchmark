# Benchmark implementation

Python runners, offline scoring, publication builders, plotting, validators and
tests are grouped here. The root README contains the current analysis and graphs.

From the repository root:

```sh
python3 scripts/validate.py
python3 scripts/validate_native_images.py
python3 scripts/validate_fastino_images.py
python3 scripts/validate_repository_layout.py
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/build_image_site.py
```

These checks do not call model providers or require API credentials. Re-scoring
correctness requires an explicitly supplied external frozen key. Publication
builders refuse to overwrite existing dated evidence.

`repo_layout.py` maps former logical paths to current physical locations.
`legacy_layout/` retains exact pre-move sources and navigation documents so
historical seals still refer to their original bytes. Runtime logs, keys,
private answers and scratch files stay outside Git.

[Current report](../README.md) · [Data](../data/README.md) · [Results](../results/README.md)
