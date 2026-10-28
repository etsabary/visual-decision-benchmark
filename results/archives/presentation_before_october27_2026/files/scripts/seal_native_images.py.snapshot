"""Create a new release seal once; never rewrite an existing published seal."""
from repo_layout import repo_file, frozen_file
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=repo_file('native_images_2026-10-20', root=ROOT)
SOURCES=('image_models_2026_10_20.py','test_image_models_2026_10_20.py',
    'analyze_native_images.py','test_native_analysis.py','plot_native_images.py',
    'publish_native_images.py','image_publication_history.py','validate_native_images.py',
    'test_native_publication.py','score_native_images.py','seal_native_images.py','build_image_site.py',
    'README.md','native_image_analysis.md','METHODOLOGY.md','RELEASE_NOTES.md','CITATION.cff',
    'validate.py','report.html','index.html','requirements-image-reports.txt','.github/workflows/image-release.yml','.gitignore')

def seal():
    destination=DATA/'checksums.json';assert not destination.exists(),'Do not overwrite a release seal'
    paths=[repo_file(name, root=ROOT) for name in SOURCES]+[p for p in DATA.rglob('*') if p.is_file()]+[p for p in (repo_file('archive_2026-10-16', root=ROOT)).rglob('*') if p.is_file()]
    files={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    destination.write_text(json.dumps({'version':'native-images-20261020-v1','files':files},indent=2)+'\n')
    print(json.dumps({'sealed_files':len(files)}))

if __name__=='__main__':seal()
