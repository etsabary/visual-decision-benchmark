"""Current physical paths; exact pre-layout bytes for frozen historical audits."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'scripts/layout_manifest.json'


@lru_cache(maxsize=4)
def _manifest(path,mtime):return json.loads(path.read_text())
def layout_manifest():return _manifest(MANIFEST,MANIFEST.stat().st_mtime_ns)


def repo_file(path,*,root=None):
    root=ROOT if root is None else Path(root);path=Path(path)
    if root!=ROOT:return root/path
    if path.is_absolute():
        try:path=path.relative_to(ROOT)
        except ValueError:return path
    if not path.parts:return ROOT
    # Already-physical high-level paths must not be mapped a second time.
    if path.parts[0] in ('scripts','documents','docs'):return ROOT/path
    if path.parts[0]=='results' and len(path.parts)>1 and path.parts[1] in ('releases','archives','figures','original_2026-10-15'):return ROOT/path
    if path.parts[0]=='data' and len(path.parts)>1 and path.parts[1] in ('images','questions'):return ROOT/path
    manifest=layout_manifest();name=path.parts[0]
    if len(path.parts)==1 and name in manifest['source_files']:return ROOT/'scripts'/name
    prefix=manifest['prefixes'].get(name,name)
    return ROOT/prefix/Path(*path.parts[1:])


def frozen_file(path):
    path=Path(path)
    if path.is_absolute():
        try:path=path.relative_to(ROOT)
        except ValueError:return path
    name=path.as_posix();manifest=layout_manifest()
    if name.startswith('scripts/') and path.name in manifest['source_files']:name=path.name
    else:name=logical_relative(ROOT/path).as_posix()
    entry=manifest['preserved_sources'].get(name)
    if entry:
        saved=ROOT/entry['path'];assert saved.resolve().is_relative_to((ROOT/'scripts/legacy_layout').resolve())
        assert sha256(saved.read_bytes()).hexdigest()==entry['sha256'],name
        return saved
    return repo_file(path)


def logical_relative(path):
    relative=Path(path).relative_to(ROOT);text=relative.as_posix();manifest=layout_manifest()
    if len(relative.parts)==2 and relative.parts[0]=='scripts' and relative.name in manifest['source_files']:return Path(relative.name)
    for old,new in sorted(manifest['prefixes'].items(),key=lambda v:-len(v[1])):
        if text==new or text.startswith(new+'/'):return Path(old+text[len(new):])
    return relative
