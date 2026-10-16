"""Seal reviewed documentation/capability additions without changing image evidence."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDITABLE = {'README.md', 'RELEASE_NOTES.md', 'test_benchmark.py', 'freeze_checksums.py'}
ADDED = {'data/october_16_capabilities.json', 'data/october_16_compatibility_probes.jsonl', 'freeze_checksums.py'}


def main():
    seal = json.loads((ROOT / 'checksums.json').read_text())
    for name, expected in seal['files'].items():
        if name not in EDITABLE and name not in ADDED:
            assert sha256((ROOT / name).read_bytes()).hexdigest() == expected, 'Original evidence changed: ' + name
    names = set(seal['files']) | ADDED
    seal['version'] = 'visual-decision-public-2026-10-16-capability-review-v2'
    seal['files'] = {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}
    (ROOT / 'checksums.json').write_text(json.dumps(seal, indent=2) + '\n')
    print('Sealed capability review; original scored data and images unchanged')


if __name__ == '__main__':
    main()
