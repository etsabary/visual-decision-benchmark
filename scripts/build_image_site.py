"""Stage only an explicit public-file allowlist for GitHub Pages."""
from repo_layout import repo_file, frozen_file
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
FILES=('report.html','index.html','gallery.html','README.md','METHODOLOGY.md','RELEASE_NOTES.md',
       'THIRD_PARTY_NOTICES.md','CITATION.cff','LICENSE','checksums.json')
DIRECTORIES=('native_images_2026-10-20','fastino_2026-10-23','images','results','figures','archive_2026-10-16')

def build():
    out=repo_file('_site', root=ROOT);out.mkdir(exist_ok=True)
    for name in FILES:shutil.copy2(repo_file(name, root=ROOT),out/name)
    for name in DIRECTORIES:shutil.copytree(repo_file(name, root=ROOT),out/name,dirs_exist_ok=True)
    # Keep original public URLs without copying newly nested images a second
    # time under data/. Only the original data files are website data exports.
    data=out/'data';data.mkdir(exist_ok=True)
    for path in (ROOT/'data').iterdir():
        if path.is_file():shutil.copy2(path,data/path.name)
    questions=out/'questions';questions.mkdir(exist_ok=True)
    for path in repo_file('questions').iterdir():
        if path.is_file():
            # Old site URLs use the original relative navigation. GitHub files
            # have mechanically rebased links for their new data/questions/ home.
            shutil.copy2(frozen_file(path),questions/path.name)
    (out/'.nojekyll').touch()
    assert not (out/'runs').exists() and not any(p.name.startswith('.env') for p in out.rglob('*'))
    print('Staged explicit public allowlist in _site')

if __name__=='__main__':build()
