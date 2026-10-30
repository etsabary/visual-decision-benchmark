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
    local=ROOT/'results/releases/local_images_2026-10-25'
    if local.exists():
        shutil.copytree(local,out/local.name,dirs_exist_ok=True)
        shutil.copy2(ROOT/'documents/LOCAL_IMAGE_RUNS.md',out/'LOCAL_IMAGE_RUNS.md')
    reference=ROOT/'results/releases/llm_reference_2026-10-25'
    if reference.exists():
        shutil.copytree(reference,out/reference.name,dirs_exist_ok=True)
        shutil.copy2(ROOT/'documents/LLM_IMAGE_REFERENCES.md',out/'LLM_IMAGE_REFERENCES.md')
    celeris=ROOT/'results/releases/celeris_2026-10-26'
    if celeris.exists():
        shutil.copytree(celeris,out/celeris.name,dirs_exist_ok=True)
        shutil.copy2(ROOT/'documents/CELERIS_IMAGE_RUN.md',out/'CELERIS_IMAGE_RUN.md')
        shutil.copy2(ROOT/'docs/sitemap.xml',out/'sitemap.xml')
    updates=ROOT/'results/releases/native_updates_2026-10-27'
    if updates.exists():
        shutil.copytree(updates,out/updates.name,dirs_exist_ok=True)
        shutil.copy2(ROOT/'documents/OCTOBER27_UPDATES.md',out/'OCTOBER27_UPDATES.md')
    screens=ROOT/'results/releases/local_m2_screens_2026-10-28'
    if screens.exists():
        target=out/'results/releases/local_m2_screens_2026-10-28'
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(screens,target,dirs_exist_ok=True)
    subset=ROOT/'results/releases/single_image_subset_2026-10-29'
    if subset.exists():shutil.copytree(subset,out/subset.name,dirs_exist_ok=True)
    october30=ROOT/'results/releases/native_updates_2026-10-30'
    if october30.exists():shutil.copytree(october30,out/october30.name,dirs_exist_ok=True)
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
