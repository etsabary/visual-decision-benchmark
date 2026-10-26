"""Reproduce exploratory Decisions confidence thresholds with an external key."""
from repo_layout import repo_file, frozen_file
import argparse
import json
from pathlib import Path
from benchmark import ROOT, rows, confidence_profile
from score import load_key

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--answer-key',required=True,type=Path)
    args=parser.parse_args()
    result=confidence_profile(load_key(args.answer_key),rows(repo_file('data/attempts.jsonl', root=ROOT)))
    published=json.loads((repo_file('results/selective_accuracy.json', root=ROOT)).read_text())
    assert result==published['models'],'Does not reproduce the published key reference'
    print(json.dumps({'status':'MATCHES_PUBLISHED_REFERENCE','models':result},indent=2))
