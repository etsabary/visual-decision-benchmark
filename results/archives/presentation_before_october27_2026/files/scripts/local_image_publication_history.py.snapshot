"""Resolve sealed Fastino presentation bytes after the local-image update."""
from hashlib import sha256
import json
from pathlib import Path

from repo_layout import ROOT

ARCHIVE = ROOT / 'results/archives/fastino_2026-10-23_presentation'


def prior_path(name):
    name = str(name)
    manifest = ARCHIVE / 'manifest.json'
    entries = json.loads(manifest.read_text())['files'] if manifest.exists() else {}
    entry = entries.get(name)
    if not entry:
        return ROOT / name
    path = ROOT / entry['path']
    assert sha256(path.read_bytes()).hexdigest() == entry['sha256'], name
    return path
