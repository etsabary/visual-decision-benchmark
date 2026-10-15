"""Re-score saved responses using an explicitly supplied external answer key."""
import argparse
import csv
import json
from pathlib import Path
from benchmark import ROOT, rows, score


def load_key(path):
    path=Path(path)
    if path.suffix=='.csv':
        with path.open(newline='') as handle:records=list(csv.DictReader(handle))
    else:records=rows(path)
    result={r['candidate_id']:str(r['correct_option_id']) for r in records}
    if len(result)!=len(records):raise ValueError('Duplicate key ID')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--answer-key',required=True,type=Path,help='External CSV or JSONL: candidate_id, correct_option_id')
    args=parser.parse_args()
    result=score(load_key(args.answer_key))
    published=json.loads((ROOT/'results/summary.json').read_text())
    for model,value in result.items():
        for field in ('correct_first','usable_first','eventual_correct'):
            if value[field]!=published['models'][model][field]:raise ValueError('Key differs from published reference: '+model+' '+field)
    print(json.dumps({'status':'MATCHES_PUBLISHED_REFERENCE','models':result},indent=2))
