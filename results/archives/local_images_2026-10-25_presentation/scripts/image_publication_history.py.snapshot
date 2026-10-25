"""Preserve the original release's presentation without changing its sealed data."""
from repo_layout import repo_file, frozen_file
from hashlib import sha256
import json
from pathlib import Path
import shutil

ARCHIVE='archive_2026-10-16'
REPLACED=('README.md','METHODOLOGY.md','RELEASE_NOTES.md','validate.py','CITATION.cff','.gitignore')

def historical_path(root,name):
    archived=repo_file(ARCHIVE, root=Path(root))/name
    return archived if archived.is_file() else frozen_file(repo_file(name, root=Path(root)))

def preserve(root):
    root=Path(root);seal=json.loads((repo_file('checksums.json', root=root)).read_text())
    for name in REPLACED:
        target=repo_file(ARCHIVE, root=root)/name
        if target.exists():
            assert sha256(target.read_bytes()).hexdigest()==seal['files'][name]
            continue
        source=repo_file(name, root=root)
        assert sha256(source.read_bytes()).hexdigest()==seal['files'][name]
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)

if __name__=='__main__':preserve(Path(__file__).resolve().parents[1])
