"""Check the slim physical layout and exact pre-layout source snapshots."""
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit
from repo_layout import ROOT,MANIFEST,repo_file,frozen_file


def validate():
    m=json.loads(MANIFEST.read_text())
    assert m['version']=='image-high-level-layout-20261023-v1'
    assert not list(ROOT.glob('*.py')) and {p.name for p in ROOT.glob('*.md')}=={'README.md'}
    tracked=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    entries={name.split('/')[0] for name in tracked if name and (ROOT/name).exists()}
    assert entries==set(m['root_entries']) and len(entries)==11,entries
    for old,entry in m['preserved_sources'].items():
        p=ROOT/entry['path'];assert sha256(p.read_bytes()).hexdigest()==entry['sha256'],old
        assert frozen_file(ROOT/old)==p,old
    for name,h in m['current_files'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    sources={p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py')}
    assert sources<=m['current_files'].keys()
    for p in (ROOT/'scripts').glob('*.py'):compile(p.read_text(),str(p),'exec')
    for p in [ROOT/'README.md',ROOT/'scripts/README.md',ROOT/'data/README.md',ROOT/'results/README.md',*sorted((ROOT/'documents').glob('*.md'))]:
        for target in re.findall(r'\]\(([^\s)]+)\)',p.read_text()):
            url=urlsplit(target)
            if not url.scheme and not url.netloc and url.path:assert (p.parent/url.path).exists(),(p,target)
    print('PASS: 11 high-level root entries; scripts, documents, questions/images, dated results and stable website paths separated; exact historical snapshots preserved.')
    return m


if __name__=='__main__':validate()
