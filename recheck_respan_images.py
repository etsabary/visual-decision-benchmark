"""Separate, answer-blind repeat of the stopped Respan image route.

Original execution code, pixels, question order, provider pin and speed cutoff
are reused unchanged. No inference without --execute; no automatic publication.
"""
import argparse
from pathlib import Path

import image_models_2026_10_20 as original

ROOT=original.ROOT
BASELINE=original.OUT/'respan02'
REPEAT=ROOT/'runs/respan_image_recheck_2026-10-20_01'
BASE_SOFTWARE=original.SOFTWARE
bind_original=original.bound


def repeat_manifest(value):
    return {**value,'version':'respan-image-repeat-20261020-01',
        'concurrency':'One serial Respan stream, no concurrent model trials in this repeat',
        'publication_authorized':False,
        'repeat_policy':'Preserve the original stopped run; no best-of-two selection or pooled partial accuracy',
        'repeat_of_stop_receipt_sha256':original.digest(BASELINE/'stop_receipt.json'),
        'reason':'User requested another run to check whether earlier latency was transient'}


def bind_repeat(path,value):
    if Path(path).name=='manifest.json':value=repeat_manifest(value)
    return bind_original(path,value)


def configure():
    original.OUT=REPEAT
    original.SOFTWARE=BASE_SOFTWARE+('recheck_respan_images.py','test_recheck_respan_images.py')
    original.bound=bind_repeat


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group();group.add_argument('--execute',action='store_true');group.add_argument('--validate',action='store_true')
    args=p.parse_args();configure()
    if args.execute:original.execute('respan02')
    elif args.validate:original.validate('respan02')
    else:print('Dry run: separate output in '+str(REPEAT.relative_to(ROOT))+'; original algorithm, maximum200, stop above2s median from20 first attempts; no inference calls.')
