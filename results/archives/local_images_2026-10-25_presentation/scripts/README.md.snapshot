# Benchmark implementation

Python runners, offline scoring, publication builders, plotting, validators and
tests are grouped here. The root README contains the current analysis and graphs.

From the repository root:

```sh
python3 scripts/validate.py
python3 scripts/validate_native_images.py
python3 scripts/validate_fastino_images.py
python3 scripts/validate_local_images_2026_10_25.py
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

`publish_local_images_2026_10_25.py` builds the 17-route publication offline from
the sealed local capture and an explicit external key; it performs no inference.
`validate_local_images_2026_10_25.py` checks old-record preservation, answer-free
local timings, PNG bindings, aggregate/category coverage, colours and mirrors.
`local_image_protocol.py` reproduces ordered payloads and public PNG derivatives
with Pillow 12.3.0; see [the local run protocol](../documents/LOCAL_IMAGE_RUNS.md).
The local-image publisher's `--seal` operation binds the final reviewed output
and current layout. It refuses to overwrite an existing dated seal.

[Current report](../README.md) · [Data](../data/README.md) · [Results](../results/README.md)
