"""Answer-free local-image payloads and explicit PNG reproduction; no transport."""
import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path


def payload(model, question, image_bytes):
    return dict(model=model, state='', images=[base64.b64encode(raw).decode() for raw in image_bytes],
        questions={'decision': dict(type='choice', instructions=question['question'] + '\n\nRules: ' + question['rules'],
            criteria={o['id']: o['text'] for o in question['options']})}, keep_alive='10m')


def wire(body):
    # The captured LAN executor used JSON's default ASCII escaping. Historical
    # hosted payloads use a different serializer; preserve the actual LAN bytes.
    return json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def reproduce_images(root, destination, variant):
    """Reproduce public inputs; six withheld originals remain unavailable."""
    from PIL import Image
    import PIL
    assert PIL.__version__ == variant['pillow_version'], 'Use the captured Pillow version for exact PNG hashes'
    destination.mkdir(parents=True, exist_ok=True)
    reproduced = 0
    for aid, asset in variant['assets'].items():
        if asset['original_public_path'] is None:
            continue
        original = root / asset['original_public_path']
        assert sha256(original.read_bytes()).hexdigest() == asset['original_sha256']
        target = destination / (aid + '.png')
        if asset['converted']:
            with Image.open(original) as image:
                image.convert('RGB').save(target, format='PNG', optimize=False, compress_level=6)
        else:
            target.write_bytes(original.read_bytes())
        assert sha256(target.read_bytes()).hexdigest() == asset['sha256'], aid
        with Image.open(target) as image:
            assert sha256(image.convert('RGB').tobytes()).hexdigest() == asset['decoded_rgb_sha256'], aid
        reproduced += 1
    return reproduced


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant-manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    count = reproduce_images(root, args.output, json.loads(args.variant_manifest.read_text()))
    print(f'Reproduced {count} public PNG inputs; six source-rights exclusions remain withheld.')
