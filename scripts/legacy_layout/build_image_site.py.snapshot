"""Stage only an explicit public-file allowlist for GitHub Pages."""
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
FILES=('report.html','index.html','gallery.html','README.md','METHODOLOGY.md','RELEASE_NOTES.md',
       'THIRD_PARTY_NOTICES.md','CITATION.cff','LICENSE','checksums.json')
DIRECTORIES=('native_images_2026-10-20','questions','images','data','results','figures','archive_2026-10-16')

def build():
    out=ROOT/'_site';out.mkdir(exist_ok=True)
    for name in FILES:shutil.copy2(ROOT/name,out/name)
    for name in DIRECTORIES:shutil.copytree(ROOT/name,out/name,dirs_exist_ok=True)
    (out/'.nojekyll').touch()
    assert not (out/'runs').exists() and not any(p.name.startswith('.env') for p in out.rglob('*'))
    print('Staged explicit public allowlist in _site')

if __name__=='__main__':build()
