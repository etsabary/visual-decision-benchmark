"""Reproduce exploratory Decisions confidence thresholds with an external key."""
import argparse
import json
from pathlib import Path
from benchmark import ROOT, rows, confidence_profile
from score import load_key

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--answer-key',required=True,type=Path)
    args=parser.parse_args()
    result=confidence_profile(load_key(args.answer_key),rows(ROOT/'data/attempts.jsonl'))
    published=json.loads((ROOT/'results/selective_accuracy.json').read_text())
    assert result==published['models'],'Does not reproduce the published key reference'
    print(json.dumps({'status':'MATCHES_PUBLISHED_REFERENCE','models':result},indent=2))
