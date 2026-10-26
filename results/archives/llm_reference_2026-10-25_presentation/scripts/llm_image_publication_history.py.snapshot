"""Resolve the exact sealed 17-route presentation after adding LLM references."""
from hashlib import sha256
import json

from repo_layout import ROOT

ARCHIVE=ROOT/'results/archives/local_images_2026-10-25_presentation'


def local_historical_path(name):
    name=str(name);manifest=ARCHIVE/'manifest.json'
    entries=json.loads(manifest.read_text())['files'] if manifest.exists() else {}
    entry=entries.get(name)
    if entry:
        path=ROOT/entry['path']
        assert sha256(path.read_bytes()).hexdigest()==entry['sha256'],name
        return path
    return ROOT/name
