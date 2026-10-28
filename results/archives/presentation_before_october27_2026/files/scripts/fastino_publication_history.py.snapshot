"""Resolve the exact October20 presentation after the Fastino update."""
from repo_layout import repo_file, frozen_file
from hashlib import sha256
import json
from pathlib import Path


def native_historical_path(root,name):
    root=Path(root)
    folder=repo_file('results/archives/native_images_2026-10-20_presentation', root=root)
    manifest=folder/'manifest.json'
    entries=json.loads(manifest.read_text())['files'] if manifest.exists() else {}
    entry=entries.get(str(name))
    if entry:
        saved=repo_file(entry['path'], root=root);assert sha256(saved.read_bytes()).hexdigest()==entry['sha256']
        return saved
    return repo_file(name, root=root)
