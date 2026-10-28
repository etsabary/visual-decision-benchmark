"""Resolve the sealed 18-route presentation after adding Celeris."""
from hashlib import sha256
import json
from repo_layout import ROOT

ARCHIVE=ROOT/'results/archives/llm_reference_2026-10-25_presentation'


def historical_path(name):
    name=str(name)
    entry=json.loads((ARCHIVE/'manifest.json').read_text())['files'].get(name)
    if entry is None:return ROOT/name
    path=ROOT/entry['path']
    assert sha256(path.read_bytes()).hexdigest()==entry['sha256'],name
    return path
